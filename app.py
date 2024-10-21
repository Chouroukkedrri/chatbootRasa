import psycopg2
from collections import Counter

def get_top_prospect_data(start_date, end_date):
    # Connection to the database
    conn = psycopg2.connect(
        dbname="birdnotes",
        user="postgres",
        password="chourouk",
        host="localhost",
        port="5432"
    )

    # Create a cursor to execute queries
    cur = conn.cursor()

    # Define the SQL query with JOIN, GROUP BY, and ORDER BY
    sql = """
    SELECT subquery.prospect_id, subquery.visit_date, SUM(subquery.order_quantity_prediction) as total_order_prediction, pr.first_name, pr.last_name
    FROM (
        SELECT v.prospect_id, v.visit_date, pop.order_quantity_prediction
        FROM visit v
        INNER JOIN prospect_order_prediction pop ON v.prospect_id = pop.prospect_id
        WHERE v.visit_date BETWEEN %s AND %s
    ) AS subquery
    INNER JOIN prospect pr ON subquery.prospect_id = pr.id
    GROUP BY subquery.prospect_id, subquery.visit_date, pr.first_name, pr.last_name
    ORDER BY total_order_prediction DESC
    LIMIT 5;
    """

    # Execute the query with the provided start and end dates
    cur.execute(sql, (start_date, end_date))

    # Fetch all the rows
    rows = cur.fetchall()

    # Close cursor and connection
    cur.close()
    conn.close()

    # Return the fetched rows
    return rows
def get_data(start_date, end_date):
    # Connection to the database
    conn = psycopg2.connect(
        dbname="birdnotes",
        user="postgres",
        password="chourouk",
        host="localhost",
        port="5432"
    )

    # Create a cursor to execute queries
    cur = conn.cursor()

    # Define the SQL query with placeholders for start and end dates
    sql = """
    SELECT visits_products.comment_rating, visit.visit_date
    FROM public.visits_products
    INNER JOIN visit ON visits_products.visit_id = visit.id
    WHERE comment_rating IS NOT NULL
      AND visit.visit_date BETWEEN %s AND %s
    ORDER BY visits_products.id DESC;
    """

    # Execute the SQL query with the provided start and end dates
    cur.execute(sql, (start_date, end_date))
    rows = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return rows

def calculate_percentage(data):
    # Preprocess comment ratings to unify spellings
    corrected_data = [(comment.replace("Presentation", "Présentation")
                       .replace("Reclamation", "Réclamation"), date) for comment, date in data]

    # Count occurrences of each corrected comment rating
    comment_count = Counter(comment for comment, _ in corrected_data)
    total_comments = len(corrected_data)

    # Calculate the percentage for each corrected comment rating
    percentages = {}
    for comment, count in comment_count.items():
        percentage = (count / total_comments) * 100
        percentages[comment] = percentage

    return percentages

def generate_text(percentages):
    # Generate text based on the percentages
    text = ""
    for comment, percentage in percentages.items():
        if percentage < 5:
            text += f"peu de {comment}, "
        elif percentage > 15:
            text += f"beaucoup de {comment}, "

    return text
def execute_sql_query(sql_query):
    # Connection to the database
    conn = psycopg2.connect(
        dbname="birdnotes",
        user="postgres",
        password="chourouk",
        host="localhost",
        port="5432"
    )

    # Create a cursor to execute queries
    cur = conn.cursor()

    try:
        # Execute the SQL query
        cur.execute(sql_query)
        result = cur.fetchone()[0]  # Assuming the query returns a single value

    except (Exception, psycopg2.Error) as error:
        raise Exception(f"Error while executing SQL query: {error}")

    finally:
        # Close cursor and connection
        if conn:
            cur.close()
            conn.close()

    return result

def main():
    # Prompt the user for the start and end dates
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    # Fetch top prospect data based on the specified date range
    top_prospect_data = get_top_prospect_data(start_date, end_date)

    if top_prospect_data:
        print("Il est recommandé de visiter les prospects suivants:")
        for prospect in top_prospect_data:
            print(f"  {prospect[3]} {prospect[4]}")

    # Fetch data based on the specified date range
    data = get_data(start_date, end_date)

    # Calculate the percentage based on the fetched data
    percentages = calculate_percentage(data)

    # Generate text based on the percentages
    text = generate_text(percentages)

    # Print "Pas de commentaires" if generated text is empty
    if not text:
        text = "Pas de commentaires"

    print("Generated text:", text)

if __name__ == "__main__":
    main()
