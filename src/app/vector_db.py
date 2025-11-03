from sentence_transformers import SentenceTransformer
import psycopg2, json

def connect_to_db():
        conn = psycopg2.connect(
            dbname="pgql",
            user="{username}", # admin
            password="{password}",
            host="localhost",
            port="5432"
        )
        cur=conn.cursor()
        return conn, cur

def embedding_model():
    model=SentenceTransformer('Snowflake/snowflake-arctic-embed-l-v2.0')
    # content='Introducing a Revolutionary Platform for Tech Startup Creation and Investments.'
    # embedding=model.encode(content).tolist()
    # print(embedding)
    # print(len(embedding))
    return model

def insert_to_db(content):
    embedding=model.encode(content).tolist()
    cur=conn.cursor()
    cur.execute('''
        insert into documents (content, embedding)
        values (%s, %s);
    ''', (content, embedding))
    conn.commit()
    cur.close()

def add_docs(docs):
    for doc in docs:
        insert_to_db(doc)

# Querying the database for similar documents
def query_postgresql(query, top_k=3):
    cur=conn.cursor()
    query_embedding=model.encode(query).tolist() # query_embedding=json.dumps(model.encode(query).tolist())
    cur.execute('''
        select content, embedding <=> %s::vector as similarity_score
        from documents
        order by similarity_score asc
        limit %s;
    ''', (query_embedding, top_k))
    results=cur.fetchall()
    cur.close()
    # conn.close()
    return [r[0] for r in results] # results

# docs=['LunaSpace’s mission is to create AI systems that can accurately understand the universe and aid humanity in its pursuit of knowledge. Our team is small, highly motivated, and focused on engineering excellence. This organization is for individuals who appreciate challenging themselves and thrive on curiosity. We operate with a flat organizational structure. All employees are expected to be hands-on and to contribute directly to the company’s mission. Leadership is given to those who show initiative and consistently deliver excellence. Work ethic and strong prioritization skills are important. All engineers are expected to have strong communication skills. They should be able to concisely and accurately share knowledge with their teammates.',
#     "About the role We're looking for exceptional multimedia engineers and product thinkers who want to make Grok's realtime avatar products the best in the world.", 
#     "What You'll Do - Make Grok's realtime avatar products fast, scalable, and reliable. Help push forward audio and gameplay research and deploy breakthrough innovations to millions of users. Obsess over every millisecond and byte, ensuring end-to-end quality and performance at scale across a rich suite of products and user platforms.", 
#     "Who You Are - Well-versed in low-latency systems and protocols like WebSocket and WebRTC. Expert in Python, and preferably proficient in Rust. Some iOS experience preferable. In-depth knowledge and experience building high performance media processing pipelines. Obsessed with media quality, performance, and product experience.", 
#     "Tech Stack - Python, Rust, WebSocket, WebRTC", 
#     "Location - The role is based in Palo Alto. Candidates are expected to be located near the Bay Area or open to relocation.", 
#     "Annual Salary Range - $180,000 - $440,000 USD", 
#     "Benefits - Base salary is just one part of our total rewards package at xAI, which also includes equity, comprehensive medical, vision, and dental coverage, access to a 401(k) retirement plan, short & long-term disability insurance, life insurance, and various other discounts and perks."]
conn, cur=connect_to_db()
model=embedding_model()
# add_docs(docs)
