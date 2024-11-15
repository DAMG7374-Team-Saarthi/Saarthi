from neo4j import GraphDatabase
import requests
from neo4j.exceptions import CypherSyntaxError
import re
import os

def connect_to_graph_db(uri, auth):
    # print("--------- connect_to_graph_db --------------")
    driver = GraphDatabase.driver(uri, auth=auth)
    verify_connection(driver)
    return driver

def verify_connection(driver):
    # print("--------- verify_connection --------------")
    with driver.session() as session:
        try:
            session.run("RETURN 1")  # Simple query to check connection
            print("Connection to the database was successful.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

def close_graph_db(driver):
    driver.close()

def fetch_schema(driver):
    # print("--------- fetch_schema --------------")
    schema_info = {"Nodes": [], "Relationships": []}

    with driver.session() as session:
        # Fetch node labels and properties
        nodes_result = session.run("CALL apoc.meta.schema()")
        for record in nodes_result:
            schema = record["value"]
            for node, details in schema.items():
                if details.get("type") == "node":
                    schema_info["Nodes"].append({
                        "label": node,
                        "properties": list(details["properties"].keys())
                    })
                elif details.get("type") == "relationship":
                    schema_info["Relationships"].append({
                        "type": node,
                        "properties": list(details["properties"].keys())
                    })
    # print("schema_info:",schema_info)
    return schema_info

def format_schema_text(schema):
    # print("--------- format_schema_text --------------" )
    schema_text = "Nodes:\n"
    for node in schema["Nodes"]:
        schema_text += f" - {node['label']} with properties {node['properties']}\n"

    schema_text += "\nRelationships:\n"
    for rel in schema["Relationships"]:
        schema_text += f" - {rel['type']} with properties {rel['properties']}\n"
    # print("--------- end_format_schema_text --------------" )
    return schema_text

def parse_user_preferences(preferences_str):
    preferences = {}
    area_match = re.search(r"Area:\s*([a-zA-Z\s]+)", preferences_str)
    budget_match = re.search(r"Budget:\s*(\d+)-(\d+)", preferences_str)
    bedrooms_match = re.search(r"Bedrooms:\s*(\d+)", preferences_str)
    bathrooms_match = re.search(r"Bathrooms:\s*(\d+)", preferences_str)
    food_match = re.search(r"Food Preferences:\s*([a-zA-Z\s]+)", preferences_str)
    park_match = re.search(r"Park:\s*(Yes|No)", preferences_str)

    if area_match:
        preferences["area"] = area_match.group(1).strip()
    if budget_match:
        preferences["budget_min"] = int(budget_match.group(1))
        preferences["budget_max"] = int(budget_match.group(2))
    if bedrooms_match:
        preferences["bedrooms"] = int(bedrooms_match.group(1))
    if bathrooms_match:
        preferences["bathrooms"] = int(bathrooms_match.group(1))
    if food_match:
        food_pref = food_match.group(1).strip().lower()
        cuisines = ["indian", "korean", "mexican", "chinese", "italian", "japanese", "thai", "french"]
        for cuisine in cuisines:
            if cuisine in food_pref:
                preferences["food"] = cuisine.capitalize()
                break
    if park_match:
        preferences["park"] = park_match.group(1).strip()
        
    
    return preferences

def create_cypher_query(preferences):
    # Construct the Cypher query based on extracted preferences
    # query = "MATCH (a:Apartment) WHERE "
    query = "MATCH (a:Apartment) "
    conditions = []

    if "area" in preferences:
        conditions.append(f'a.apt_address CONTAINS "{preferences["area"]}"')
    if "budget_min" in preferences and "budget_max" in preferences:
        conditions.append(f'a.apt_rent >= {preferences["budget_min"]}')
        conditions.append(f'a.apt_rent <= {preferences["budget_max"]}')
    if "bedrooms" in preferences:
        conditions.append(f'a.apt_bedroom_count = {preferences["bedrooms"]}')
    if "bathrooms" in preferences:
        conditions.append(f'a.apt_bathroom_count = {preferences["bathrooms"]}')
    if "food" in preferences:
        query += "-[:has_nearby_restaurant]->(r:Restaurant) "
        conditions.append(f'r.restaurant_cuisine CONTAINS "{preferences["food"]}"')

    # Park (Yes/No)
    if "park" in preferences:
        if preferences["park"].lower() == "yes":
            # query += "a:Apartment)-[:has_nearby_park]->(p:park) "
            query += "-[:has_nearby_park]->(p:park) "
        # else:
        #     query += "OPTIONAL MATCH (a)-[:NEARBY]->(p:Park {type: 'Park'}) "
        #     where_conditions.append("p IS NULL")


    # Combine conditions with "AND"
    query += "WHERE" + " AND ".join(conditions)
    query += " RETURN a"
    print(query)
    return query

def get_system_message(schema):
    # print("--------- get_system_message --------------")
    return f"""
    Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
    Instructions:
    Use only the provided node labels, relationship types, and properties.
    Do not use any other node labels, relationship types, or properties that are not provided.
    Schema:
    {format_schema_text(schema)}

    Do not include any explanations or apologies in your responses.
    """

def query_database(driver, cypher_query, params={}):
    # print("--------- query_database --------------")
    clean_query = cypher_query.replace("```cypher", "").replace("```", "").strip().split(';')[0].strip()

    print(clean_query)
    # Check for any destructive keywords
    destructive_keywords = ["DELETE", "DETACH DELETE", "DROP", "CREATE", "SET", "MERGE", "REMOVE"]
    if any(re.search(rf"\b{keyword}\b", clean_query, re.IGNORECASE) for keyword in destructive_keywords):
        raise ValueError("Query contains schema-altering or destructive operations and is not allowed.")

    with driver.session() as session:
        result = session.run(clean_query, params)
        return [dict(record) for record in result]

def construct_cypher(preferences_str, schema, openai_api_key):
    # print("--------- construct_cypher --------------")
    preferences = parse_user_preferences(preferences_str)
    cypher_query = create_cypher_query(preferences)

    messages = [
        {"role": "system", "content": get_system_message(schema)},
        {"role": "user", "content": cypher_query},
    ]


    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-sonar-small-128k-chat",  # Adjust model if needed
        "messages": messages,
    }
    url = "https://api.perplexity.ai/chat/completions"
    # response = requests.post("https://api.perplexity.ai/v1/chat/completions", json=payload, headers=headers)
    response = requests.request("POST", url, json=payload, headers=headers)

    # print("response", response)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error from model API: {response.status_code} {response.text}")

def run_query(uri, auth, openai_api_key, question):
    # print("--------- run_query --------------")
    driver = connect_to_graph_db(uri, auth)
    schema = fetch_schema(driver)
    cypher_query = construct_cypher(question, schema, openai_api_key)
    # print("Generated Cypher Query:", cypher_query)
    try:
        return query_database(driver, cypher_query)
    except CypherSyntaxError as e:
        print(f"Error executing query: {e}")
    finally:
        close_graph_db(driver)

if __name__ == "__main__":
   
    openai_key = os.getenv("OPENAI_API_KEY")
    neo4j_URI = os.getenv("NEO4J_URI")
    neo4j_AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
   
    question = "Collected User Preferences:Area: Queensberry,Budget: 2500-3000,Bedrooms: 1,Bathrooms: 1,Food Preferences: Indian food places nearby,Park: No"
    results = run_query(neo4j_URI, neo4j_AUTH, openai_key, question)
    print("Query Results:", results)




