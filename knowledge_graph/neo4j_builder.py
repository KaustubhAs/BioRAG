# from neo4j import GraphDatabase
# from schema import GraphSchema

# class Neo4jGraphBuilder:
#     def __init__(self, uri, username, password):
#         self.driver = GraphDatabase.driver(uri, auth=(username, password))

#     def close(self):
#         self.driver.close()

#     def create_constraints(self):
#         with self.driver.session() as session:
#             # Create constraints for Disease and Symptom nodes
#             session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (d:{GraphSchema.DISEASE}) REQUIRE d.{GraphSchema.NAME} IS UNIQUE")
#             session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (s:{GraphSchema.SYMPTOM}) REQUIRE s.{GraphSchema.NAME} IS UNIQUE")

#     def clear_database(self):
#         with self.driver.session() as session:
#             session.run("MATCH (n) DETACH DELETE n")

#     def create_disease_nodes(self, diseases, embeddings=None):
#         with self.driver.session() as session:
#             for i, disease in enumerate(diseases):
#                 embedding = embeddings[i].tolist() if embeddings is not None else None
#                 session.run(
#                     f"""
#                     CREATE (d:{GraphSchema.DISEASE} {{
#                         {GraphSchema.NAME}: $name,
#                         {GraphSchema.EMBEDDING}: $embedding
#                     }})
#                     """,
#                     name=disease,
#                     embedding=embedding
#                 )

#     def create_symptom_nodes(self, symptoms, embeddings=None):
#         with self.driver.session() as session:
#             for i, symptom in enumerate(symptoms):
#                 embedding = embeddings[i].tolist() if embeddings is not None else None
#                 session.run(
#                     f"""
#                     CREATE (s:{GraphSchema.SYMPTOM} {{
#                         {GraphSchema.NAME}: $name,
#                         {GraphSchema.EMBEDDING}: $embedding
#                     }})
#                     """,
#                     name=symptom,
#                     embedding=embedding
#                 )

#     def create_relationships(self, relationships):
#         with self.driver.session() as session:
#             for rel in relationships:
#                 session.run(
#                     f"""
#                     MATCH (d:{GraphSchema.DISEASE}), (s:{GraphSchema.SYMPTOM})
#                     WHERE d.{GraphSchema.NAME} = $disease AND s.{GraphSchema.NAME} = $symptom
#                     CREATE (d)-[:{rel['type']}]->(s)
#                     """,
#                     disease=rel['source'],
#                     symptom=rel['target']
#                 )
