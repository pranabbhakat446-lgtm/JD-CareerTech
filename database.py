import sqlite3
import os
from datetime import datetime


DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "career.db"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==================================================
# ADD COLUMN IF MISSING
# ==================================================

def add_column_if_missing(
    connection,
    table_name,
    column_name,
    column_definition
):

    columns = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    existing_columns = [
        column["name"]
        for column in columns
    ]

    if column_name not in existing_columns:

        connection.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )

        print(
            f"Added column: "
            f"{table_name}.{column_name}"
        )


# ==================================================
# CREATE TABLES
# ==================================================

def create_tables():

    connection = get_db_connection()

    cursor = connection.cursor()

    # ==========================================
    # STUDENTS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            education TEXT,

            branch TEXT,

            year TEXT,

            city TEXT,

            created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================
    # INTERNSHIPS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            company TEXT NOT NULL,

            field TEXT,

            location TEXT,

            duration TEXT,

            stipend TEXT,

            eligibility TEXT,

            skills TEXT,

            description TEXT,

            apply_link TEXT,

            last_date TEXT,

            created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================
    # INTERNSHIP EXTRA COLUMNS
    # ==========================================

    internship_columns = [

        (
            "opportunity_type",
            "TEXT DEFAULT 'Internship'"
        ),

        (
            "address",
            "TEXT"
        ),

        (
            "area",
            "TEXT"
        ),

        (
            "city",
            "TEXT"
        ),

        (
            "official_website",
            "TEXT"
        ),

        (
            "source_url",
            "TEXT"
        ),

        (
            "application_url",
            "TEXT"
        ),

        (
            "verification_status",
            "TEXT DEFAULT 'Verified'"
        ),

        (
            "verified_at",
            "TEXT"
        ),

        (
            "mode",
            "TEXT DEFAULT 'Offline'"
        ),

        (
            "fee",
            "TEXT"
        ),

        (
            "category",
            "TEXT DEFAULT 'IT & Software'"
        ),

        (
            "provider_type",
            "TEXT"
        ),

        (
            "contact_phone",
            "TEXT"
        ),

        (
            "contact_email",
            "TEXT"
        ),

        (
            "map_link",
            "TEXT"
        )
    ]

    for column_name, column_definition in internship_columns:

        add_column_if_missing(
            connection,
            "internships",
            column_name,
            column_definition
        )

    # ==========================================
    # CAREER PATHS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_paths (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            category TEXT,

            description TEXT,

            skills TEXT,

            roadmap TEXT
        )
    """)

    # ==========================================
    # APPLICATIONS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            internship_id INTEGER NOT NULL,

            status TEXT DEFAULT 'Applied',

            applied_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, internship_id),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (internship_id)
                REFERENCES internships(id)
                ON DELETE CASCADE
        )
    """)

    # ==========================================
    # SAVED INTERNSHIPS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_internships (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            internship_id INTEGER NOT NULL,

            saved_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(student_id, internship_id),

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,

            FOREIGN KEY (internship_id)
                REFERENCES internships(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    connection.close()

    print()
    print("========================================")
    print(" DATABASE TABLES CREATED / UPDATED")
    print("========================================")


# ==================================================
# REMOVE OLD DEMO DATA
# ==================================================

def remove_old_demo_data():

    connection = get_db_connection()

    demo_companies = (
        "Tech Solutions",
        "CodeWorks",
        "DataTech Solutions",
        "QualitySoft",
        "NetworkPro"
    )

    placeholders = ",".join(
        ["?"] * len(demo_companies)
    )

    rows = connection.execute(
        f"""
        SELECT id
        FROM internships
        WHERE company IN ({placeholders})
        """,
        demo_companies
    ).fetchall()

    internship_ids = [
        row["id"]
        for row in rows
    ]

    if not internship_ids:

        connection.close()

        print(
            "No old demo internship data found."
        )

        return

    id_placeholders = ",".join(
        ["?"] * len(internship_ids)
    )

    # Remove saved records first

    connection.execute(
        f"""
        DELETE FROM saved_internships
        WHERE internship_id
        IN ({id_placeholders})
        """,
        internship_ids
    )

    # Remove application records

    connection.execute(
        f"""
        DELETE FROM applications
        WHERE internship_id
        IN ({id_placeholders})
        """,
        internship_ids
    )

    # Finally remove internship records

    connection.execute(
        f"""
        DELETE FROM internships
        WHERE id
        IN ({id_placeholders})
        """,
        internship_ids
    )

    connection.commit()

    connection.close()

    print(
        "Old demo internship data "
        "removed successfully."
    )


# ==================================================
# REAL VERIFIED OPPORTUNITIES
# ==================================================

def add_real_opportunities():

    connection = get_db_connection()

    opportunities = [

        # ==================================================
        # JAMSHEDPUR - PAULTECH
        # ==================================================

        (
            "Web Development Internship",
            "PaulTech Software Services Pvt Ltd.",
            "Web Development",
            "Jamshedpur",
            "2-3 Months",
            "Not specified",
            "Students from schools / engineering institutes",
            "PHP, MySQL, HTML, CSS, WordPress, Laravel, CodeIgniter",
            "Practical web development internship with project-based learning and industry exposure.",
            "https://paultechsoftwareservices.com/page/webdevelopment",
            "Not specified",
            "2026-10-02",
            "Internship",
            "34, First Floor, Pacific Height Building, Aambagan, Sakchi, Jamshedpur-831001",
            "Aambagan, Sakchi",
            "Jamshedpur",
            "https://paultechsoftwareservices.com/",
            "https://paultechsoftwareservices.com/page/webdevelopment",
            "https://paultechsoftwareservices.com/page/webdevelopment",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7209986943",
            "hr@paultechsoftwareservices.com",
            "https://www.google.com/maps/search/?api=1&query=34+Pacific+Height+Building+Aambagan+Sakchi+Jamshedpur"
        ),

        (
            "Data Analytics Internship",
            "PaulTech Software Services Pvt Ltd.",
            "Data Analytics",
            "Jamshedpur",
            "Not specified",
            "Not specified",
            "Students / learners interested in Data Analytics",
            "Python, R, SQL, Power BI, Data Analysis",
            "Industrial internship focused on data collection, cleaning, analysis and visualization.",
            "https://paultechsoftwareservices.com/page/dataanalytics",
            "Not specified",
            "2026-10-02",
            "Internship",
            "34, First Floor, Pacific Height Building, Aambagan, Sakchi, Jamshedpur-831001",
            "Aambagan, Sakchi",
            "Jamshedpur",
            "https://paultechsoftwareservices.com/",
            "https://paultechsoftwareservices.com/page/dataanalytics",
            "https://paultechsoftwareservices.com/page/dataanalytics",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7209986943",
            "hr@paultechsoftwareservices.com",
            "https://www.google.com/maps/search/?api=1&query=34+Pacific+Height+Building+Aambagan+Sakchi+Jamshedpur"
        ),

        (
            "Cloud Computing Internship",
            "PaulTech Software Services Pvt Ltd.",
            "Cloud Computing",
            "Jamshedpur",
            "Not specified",
            "Not specified",
            "Students interested in Cloud Computing",
            "AWS, Azure, GCP, Cloud Security, Networking, Storage",
            "Industrial internship covering cloud technologies and practical project exposure.",
            "https://paultechsoftwareservices.com/page/cloudcomputing",
            "Not specified",
            "2026-10-02",
            "Internship",
            "34, First Floor, Pacific Height Building, Aambagan, Sakchi, Jamshedpur-831001",
            "Aambagan, Sakchi",
            "Jamshedpur",
            "https://paultechsoftwareservices.com/",
            "https://paultechsoftwareservices.com/page/cloudcomputing",
            "https://paultechsoftwareservices.com/page/cloudcomputing",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7209986943",
            "hr@paultechsoftwareservices.com",
            "https://www.google.com/maps/search/?api=1&query=34+Pacific+Height+Building+Aambagan+Sakchi+Jamshedpur"
        ),

        (
            "HR & Marketing Internship",
            "PaulTech Software Services Pvt Ltd.",
            "HR & Marketing",
            "Jamshedpur",
            "Not specified",
            "Not specified",
            "Students / learners interested in HR and Marketing",
            "Recruitment, Employee Engagement, Digital Marketing, Content Creation",
            "Internship programme covering HR processes, marketing strategies and practical projects.",
            "https://paultechsoftwareservices.com/page/architecture",
            "Not specified",
            "2026-10-02",
            "Internship",
            "34, First Floor, Pacific Height Building, Aambagan, Sakchi, Jamshedpur-831001",
            "Aambagan, Sakchi",
            "Jamshedpur",
            "https://paultechsoftwareservices.com/",
            "https://paultechsoftwareservices.com/page/architecture",
            "https://paultechsoftwareservices.com/page/architecture",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7209986943",
            "hr@paultechsoftwareservices.com",
            "https://www.google.com/maps/search/?api=1&query=34+Pacific+Height+Building+Aambagan+Sakchi+Jamshedpur"
        ),

        # ==================================================
        # JAMSHEDPUR - TECHCODER
        # ==================================================

        (
            "Web Development Internship",
            "TechCoder Software (OPC) Pvt. Ltd.",
            "Web Development",
            "Jamshedpur",
            "Confirmed for intake",
            "Not specified",
            "BCA / B.Tech / IT background students and freshers",
            "Web Development, React, Node.js, MongoDB",
            "Practical internship programme focused on modern web development and real-world project exposure.",
            "https://techcoderservice.in/internship/",
            "Not specified",
            "2026-10-02",
            "Internship",
            "H/CC-14, Main Road, Champiya Colony, Sidhgora, Jamshedpur, Jharkhand - 831009",
            "Sidhgora",
            "Jamshedpur",
            "https://techcoderservice.in/",
            "https://techcoderservice.in/internship/",
            "https://techcoderservice.in/internship/",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7667 98 83 62",
            "info@techcoderservice.in",
            "https://www.google.com/maps/search/?api=1&query=H%2FCC-14+Sidhgora+Jamshedpur"
        ),

        (
            "AI & Automation Internship",
            "TechCoder Software (OPC) Pvt. Ltd.",
            "AI & Automation",
            "Jamshedpur",
            "Confirmed for intake",
            "Not specified",
            "Learners interested in AI and automation",
            "AI, Automation, APIs, Workflow Automation",
            "Internship track focused on AI automation concepts and practical workflow projects.",
            "https://techcoderservice.in/internship/",
            "Not specified",
            "2026-10-02",
            "Internship",
            "H/CC-14, Main Road, Champiya Colony, Sidhgora, Jamshedpur, Jharkhand - 831009",
            "Sidhgora",
            "Jamshedpur",
            "https://techcoderservice.in/",
            "https://techcoderservice.in/internship/",
            "https://techcoderservice.in/internship/",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7667 98 83 62",
            "info@techcoderservice.in",
            "https://www.google.com/maps/search/?api=1&query=H%2FCC-14+Sidhgora+Jamshedpur"
        ),

        (
            "Data & AI/ML Internship",
            "TechCoder Software (OPC) Pvt. Ltd.",
            "Data Science & AI",
            "Jamshedpur",
            "Confirmed for intake",
            "Not specified",
            "Learners interested in Data and AI/ML",
            "Data Analytics, Data Science, Machine Learning",
            "Internship programme with data and AI/ML learning tracks.",
            "https://techcoderservice.in/internship/",
            "Not specified",
            "2026-10-02",
            "Internship",
            "H/CC-14, Main Road, Champiya Colony, Sidhgora, Jamshedpur, Jharkhand - 831009",
            "Sidhgora",
            "Jamshedpur",
            "https://techcoderservice.in/",
            "https://techcoderservice.in/internship/",
            "https://techcoderservice.in/internship/",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Software Company",
            "+91 7667 98 83 62",
            "info@techcoderservice.in",
            "https://www.google.com/maps/search/?api=1&query=H%2FCC-14+Sidhgora+Jamshedpur"
        ),

        # ==================================================
        # HAZARIBAGH - NP SOFTHUB
        # ==================================================

        (
            "Full Stack Development Internship",
            "NP Softhub Solutions Pvt. Ltd.",
            "Full Stack Development",
            "Hazaribagh",
            "4-8 Weeks",
            "Performance based",
            "Students / Freshers",
            "Full Stack Development, Web Development",
            "Practical industry internship with project access, mentorship and career guidance.",
            "https://npsofthubsolutions.com/internship",
            "Not specified",
            "2026-10-02",
            "Internship",
            "Prem Nagar, Near VBU, Sindoor, Hazaribagh, Jharkhand - 825301",
            "Prem Nagar / Sindoor",
            "Hazaribagh",
            "https://npsofthubsolutions.com/",
            "https://npsofthubsolutions.com/internship",
            "https://npsofthubsolutions.com/internship",
            "Verified",
            "2026-10-02",
            "Offline / Online",
            "Not specified",
            "IT & Software",
            "IT Company",
            "+91 9431328027",
            "info@npsofthubsolutions.com",
            "https://www.google.com/maps/search/?api=1&query=Prem+Nagar+Sindoor+Hazaribagh+Jharkhand"
        ),

        (
            "AI / ML Internship",
            "NP Softhub Solutions Pvt. Ltd.",
            "AI / Machine Learning",
            "Hazaribagh",
            "Up to 3 Months",
            "Performance based",
            "Students / Freshers",
            "AI, Machine Learning",
            "Internship track for students interested in AI and machine learning.",
            "https://npsofthubsolutions.com/internship",
            "Not specified",
            "2026-10-02",
            "Internship",
            "Prem Nagar, Near VBU, Sindoor, Hazaribagh, Jharkhand - 825301",
            "Prem Nagar / Sindoor",
            "Hazaribagh",
            "https://npsofthubsolutions.com/",
            "https://npsofthubsolutions.com/internship",
            "https://npsofthubsolutions.com/internship",
            "Verified",
            "2026-10-02",
            "Offline / Online",
            "Not specified",
            "IT & Software",
            "IT Company",
            "+91 9431328027",
            "info@npsofthubsolutions.com",
            "https://www.google.com/maps/search/?api=1&query=Prem+Nagar+Sindoor+Hazaribagh+Jharkhand"
        ),

        # ==================================================
        # HAZARIBAGH - AISECT UNIVERSITY
        # ==================================================

        (
            "Computer Science & IT Internship",
            "AISECT University Jharkhand",
            "Computer Science & IT",
            "Hazaribagh",
            "Varies by programme",
            "Not specified",
            "Students / eligible university participants",
            "Computer Science, IT, Technical Skills",
            "University-supported internships, summer/winter internships and practical industry exposure.",
            "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "Not specified",
            "2026-10-02",
            "Internship",
            "Village Jonhiya, P.O. Mahesra, P.S. Daru, Hazaribag - 825301, Jharkhand",
            "Daru / Mahesra",
            "Hazaribagh",
            "https://aisectuniversityjharkhand.ac.in/",
            "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "Verified",
            "2026-10-02",
            "On Campus / Programme dependent",
            "Not specified",
            "Education & IT",
            "University",
            "8252299990",
            "info@aisectuniversityjharkhand.ac.in",
            "https://www.google.com/maps/search/?api=1&query=AISECT+University+Jharkhand+Hazaribagh"
        ),

        # ==================================================
        # BOKARO - IITTSD
        # ==================================================

        (
            "Python Training Program",
            "IITTSD - Institute of Information Technology for Training and Software Development",
            "Python",
            "Bokaro",
            "1 Month",
            "Not specified",
            "Students / learners",
            "Python, Programming, VS Code, Programming Basics",
            "Computer training programme covering Python programming and practical concepts.",
            "https://www.iittsd.in/INDEX.aspx",
            "Not specified",
            "2026-10-02",
            "Training",
            "Bokaro, Jharkhand",
            "Bokaro",
            "Bokaro",
            "https://www.iittsd.in/",
            "https://www.iittsd.in/INDEX.aspx",
            "https://www.iittsd.in/INDEX.aspx",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Training Institute",
            "+91 8797442358",
            "iittsd.in@gmail.com",
            "https://www.google.com/maps/search/?api=1&query=IITTSD+Bokaro+Jharkhand"
        ),

        (
            "Software Development Training",
            "IITTSD - Institute of Information Technology for Training and Software Development",
            "Software Development",
            "Bokaro",
            "Not specified",
            "Not specified",
            "Students / learners",
            "C, C++, Java, ASP.NET, VB.NET, C#, Python, SQL, MySQL, Oracle",
            "Training and software development services covering multiple programming and database technologies.",
            "https://www.iittsd.in/",
            "Not specified",
            "2026-10-02",
            "Training",
            "Bokaro, Jharkhand",
            "Bokaro",
            "Bokaro",
            "https://www.iittsd.in/",
            "https://www.iittsd.in/",
            "https://www.iittsd.in/",
            "Verified",
            "2026-10-02",
            "Offline",
            "Not specified",
            "IT & Software",
            "Training Institute",
            "+91 8797442358",
            "iittsd.in@gmail.com",
            "https://www.google.com/maps/search/?api=1&query=IITTSD+Bokaro+Jharkhand"
        )
    ]

    added_count = 0

    # ==================================================
    # INSERT ONLY MISSING RECORDS
    # ==================================================

    for opportunity in opportunities:

        (
            title,
            company,
            field,
            location,
            duration,
            stipend,
            eligibility,
            skills,
            description,
            apply_link,
            last_date,
            created_at,
            opportunity_type,
            address,
            area,
            city,
            official_website,
            source_url,
            application_url,
            verification_status,
            verified_at,
            mode,
            fee,
            category,
            provider_type,
            contact_phone,
            contact_email,
            map_link
        ) = opportunity

        existing = connection.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                title,
                company,
                city
            )
        ).fetchone()

        if existing:

            continue

        connection.execute(
            """
            INSERT INTO internships (

                title,
                company,
                field,
                location,
                duration,
                stipend,
                eligibility,
                skills,
                description,
                apply_link,
                last_date,
                created_at,

                opportunity_type,
                address,
                area,
                city,
                official_website,
                source_url,
                application_url,
                verification_status,
                verified_at,
                mode,
                fee,
                category,
                provider_type,
                contact_phone,
                contact_email,
                map_link

            )

            VALUES (

                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?

            )
            """,
            (
                title,
                company,
                field,
                location,
                duration,
                stipend,
                eligibility,
                skills,
                description,
                apply_link,
                last_date,
                created_at,

                opportunity_type,
                address,
                area,
                city,
                official_website,
                source_url,
                application_url,
                verification_status,
                verified_at,
                mode,
                fee,
                category,
                provider_type,
                contact_phone,
                contact_email,
                map_link
            )
        )

        added_count += 1

    connection.commit()

    print()
    print(
        f"{added_count} new real opportunities "
        f"added successfully."
    )

    # ==================================================
    # SHOW CITY COUNTS
    # ==================================================

    city_data = connection.execute(
        """
        SELECT city, COUNT(*) AS total
        FROM internships
        GROUP BY city
        ORDER BY city
        """
    ).fetchall()

    print()
    print("========================================")
    print(" CURRENT OPPORTUNITIES BY CITY")
    print("========================================")

    for row in city_data:

        print(
            f"{row['city']} = {row['total']}"
        )

    # ==================================================
    # TOTAL COUNT
    # ==================================================

    total = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM internships
        """
    ).fetchone()["total"]

    print()
    print(
        f"TOTAL OPPORTUNITIES = {total}"
    )

    connection.close()

def add_new_jharkhand_opportunities():
    """
    Add newly verified internship opportunities from
    Ranchi, Dhanbad and Deoghar.
    Existing records are not duplicated.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    opportunities = [

        # =========================
        # RANCHI - MATROP
        # =========================

        {
            "title": "Web Development Internship",
            "company": "MATROP PRIVATE LIMITED",
            "field": "Web Development",
            "location": "Ranchi",
            "duration": "2 weeks to 3 months",
            "stipend": None,
            "eligibility": "B.Tech CSE/IT, M.Tech, BCA, MCA, B.Sc IT/CS, Diploma IT/CS",
            "skills": "HTML, CSS, Bootstrap, PHP, JavaScript, Laravel, MySQL",
            "description": "Project-based internship with practical web development tasks, mentorship, weekly tasks and final project.",
            "apply_link": "https://www.matrop.com/internship",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Bisheseshwar Complex, Kokar Chowk, Ranchi, Jharkhand - 834001",
            "area": "Kokar",
            "city": "Ranchi",
            "official_website": "https://www.matrop.com/",
            "source_url": "https://www.matrop.com/internship",
            "application_url": "https://www.matrop.com/internship",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Online / Hybrid / Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 9430106005",
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "App Development Internship",
            "company": "MATROP PRIVATE LIMITED",
            "field": "Mobile App Development",
            "location": "Ranchi",
            "duration": "2 weeks to 3 months",
            "stipend": None,
            "eligibility": "IT and Computer-related students including Diploma IT/CS",
            "skills": "Mobile UI, APIs, Authentication, Form Validation",
            "description": "Practical mobile application internship covering app screens, navigation, APIs, validation and testing.",
            "apply_link": "https://www.matrop.com/internship",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Bisheseshwar Complex, Kokar Chowk, Ranchi, Jharkhand - 834001",
            "area": "Kokar",
            "city": "Ranchi",
            "official_website": "https://www.matrop.com/",
            "source_url": "https://www.matrop.com/internship",
            "application_url": "https://www.matrop.com/internship",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Online / Hybrid / Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 9430106005",
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Database & API Internship",
            "company": "MATROP PRIVATE LIMITED",
            "field": "Database / API",
            "location": "Ranchi",
            "duration": "2 weeks to 3 months",
            "stipend": None,
            "eligibility": "IT and Computer-related students including Diploma IT/CS",
            "skills": "MySQL, SQL, APIs, Database Design, Testing",
            "description": "Practical database and API internship covering MySQL, queries, API testing, documentation and QA basics.",
            "apply_link": "https://www.matrop.com/internship",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Bisheseshwar Complex, Kokar Chowk, Ranchi, Jharkhand - 834001",
            "area": "Kokar",
            "city": "Ranchi",
            "official_website": "https://www.matrop.com/",
            "source_url": "https://www.matrop.com/internship",
            "application_url": "https://www.matrop.com/internship",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Online / Hybrid / Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 9430106005",
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Networking & IT Support Internship",
            "company": "MATROP PRIVATE LIMITED",
            "field": "Networking / IT Support",
            "location": "Ranchi",
            "duration": "2 weeks to 3 months",
            "stipend": None,
            "eligibility": "IT and Computer-related students including Diploma IT/CS",
            "skills": "LAN, WiFi, Basic Routing, System Setup, Troubleshooting",
            "description": "Practical IT support internship covering system setup, LAN/WiFi, basic routing, server basics and troubleshooting.",
            "apply_link": "https://www.matrop.com/internship",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Bisheseshwar Complex, Kokar Chowk, Ranchi, Jharkhand - 834001",
            "area": "Kokar",
            "city": "Ranchi",
            "official_website": "https://www.matrop.com/",
            "source_url": "https://www.matrop.com/internship",
            "application_url": "https://www.matrop.com/internship",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Online / Hybrid / Onsite",
            "fee": None,
            "category": "Networking & IT",
            "provider_type": "Company",
            "contact_phone": "+91 9430106005",
            "contact_email": None,
            "map_link": None
        },

        # =========================
        # RANCHI - MURMU
        # =========================

        {
            "title": "Software Developer Intern",
            "company": "Murmu Software Infotech",
            "field": "Software Development",
            "location": "Ranchi",
            "duration": "Internship",
            "stipend": None,
            "eligibility": "Pursuing or completed B.Tech CSE/IT",
            "skills": "C#, .NET, JavaScript, PHP, Java, SQL, HTML, CSS",
            "description": "Software development internship involving web applications, business software, APIs and backend systems.",
            "apply_link": "https://murmusoftwareinfotech.com/hi/jobs-career/software-developer-intern-preferred-btech-cse",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Office No. 503, 5th Floor, Mall-Decore, Lalpur Chowk, Ranchi, Jharkhand - 834001",
            "area": "Lalpur",
            "city": "Ranchi",
            "official_website": "https://murmusoftwareinfotech.com/",
            "source_url": "https://murmusoftwareinfotech.com/hi/jobs-career/software-developer-intern-preferred-btech-cse",
            "application_url": "https://murmusoftwareinfotech.com/hi/jobs-career/software-developer-intern-preferred-btech-cse",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Ranchi / Remote",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 9110176498",
            "contact_email": "contactus@murmusoftwareinfotech.com",
            "map_link": None
        },

        {
            "title": "AI Developer Intern",
            "company": "Murmu Software Infotech",
            "field": "Artificial Intelligence / Machine Learning",
            "location": "Ranchi",
            "duration": "Internship",
            "stipend": None,
            "eligibility": "B.Tech AI & ML / CSE with AI interest",
            "skills": "Python, Machine Learning, Data Processing, NLP, Chatbots",
            "description": "AI developer internship involving AI/ML models, datasets, automation and AI-powered applications.",
            "apply_link": "https://murmusoftwareinfotech.com/jobs-career/ai-developer-intern-preferred-btech-in-ai-ml",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Office No. 503, 5th Floor, Mall-Decore, Lalpur Chowk, Ranchi, Jharkhand - 834001",
            "area": "Lalpur",
            "city": "Ranchi",
            "official_website": "https://murmusoftwareinfotech.com/",
            "source_url": "https://murmusoftwareinfotech.com/jobs-career/ai-developer-intern-preferred-btech-in-ai-ml",
            "application_url": "https://murmusoftwareinfotech.com/jobs-career/ai-developer-intern-preferred-btech-in-ai-ml",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Ranchi / Remote",
            "fee": None,
            "category": "AI & ML",
            "provider_type": "Company",
            "contact_phone": "+91 9110176498",
            "contact_email": "contactus@murmusoftwareinfotech.com",
            "map_link": None
        },

        # =========================
        # RANCHI - JHARKHAND IT SERVICES
        # =========================

        {
            "title": "Software & Web Development Internship",
            "company": "Jharkhand IT Services",
            "field": "Software / Web Development",
            "location": "Ranchi",
            "duration": "Varies by program",
            "stipend": None,
            "eligibility": "BE/B.Tech IT/CSE, BCA, MCA, B.Sc IT, M.Sc IT and technical students",
            "skills": "HTML, CSS, JavaScript, PHP, Web Development",
            "description": "Internship program with practical exposure in software and web development, including front-end and back-end development.",
            "apply_link": "https://jharkhanditservices.com/internship.php",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "3rd Floor, Janki Tower, Tagore Hill Road, Morabadi, Ranchi, Jharkhand - 834008",
            "area": "Morabadi",
            "city": "Ranchi",
            "official_website": "https://jharkhanditservices.com/",
            "source_url": "https://jharkhanditservices.com/internship.php",
            "application_url": "https://jharkhanditservices.com/internship.php",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Ranchi / Virtual",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 6209009007",
            "contact_email": "info@jharkhanditservices.com",
            "map_link": None
        },

        # =========================
        # RANCHI - SOFTOASIS
        # =========================

        {
            "title": "Software Development Internship",
            "company": "Softoasis Technologies Pvt. Ltd.",
            "field": "Software Development",
            "location": "Ranchi",
            "duration": "Internship",
            "stipend": None,
            "eligibility": "B.Tech/BE, BCA/MCA, Computer Science/IT students and aspiring technology professionals",
            "skills": "React, Node.js, Laravel, PHP, APIs, MySQL, PostgreSQL",
            "description": "Project-oriented internship with exposure to software development, APIs, databases, cloud and modern application engineering.",
            "apply_link": "https://softoasistech.com/careers/Internship",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Near Arunama Technical Services, Samlong, Pragati Path, Ranchi, Jharkhand - 834001",
            "area": "Samlong",
            "city": "Ranchi",
            "official_website": "https://softoasistech.com/",
            "source_url": "https://softoasistech.com/careers/Internship",
            "application_url": "https://softoasistech.com/careers/Internship",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Remote / Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Company",
            "contact_phone": "+91 9356704158",
            "contact_email": "hr@softoasistech.com",
            "map_link": None
        },

        # =========================
        # DHANBAD - FIDEST
        # =========================

        {
            "title": "IT & Software Internship",
            "company": "Fidest Skills Private Limited",
            "field": "IT / Software / Digital Marketing",
            "location": "Dhanbad",
            "duration": "3 to 6 months",
            "stipend": None,
            "eligibility": "Students and freshers interested in IT, software development or digital marketing",
            "skills": "Web Development, Graphics Designing, SEO, Digital Marketing, Software Development",
            "description": "Internship with practical exposure to web development, graphic design, digital marketing and custom software projects.",
            "apply_link": "https://www.fidestskills.in/apply-for-internship/",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Bagsuma, Govindpur, Dhanbad, Jharkhand - 828109",
            "area": "Govindpur",
            "city": "Dhanbad",
            "official_website": "https://www.fidestskills.in/",
            "source_url": "https://www.fidestskills.in/apply-for-internship/",
            "application_url": "https://www.fidestskills.in/apply-for-internship/",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Remote / Onsite",
            "fee": None,
            "category": "IT & Digital",
            "provider_type": "Company",
            "contact_phone": "+91 7250502169",
            "contact_email": "fidestskills@gmail.com",
            "map_link": None
        },

        # =========================
        # DEOGHAR - CODINGPARA
        # =========================

        {
            "title": "Web Development Intern",
            "company": "Codingpara Technologies",
            "field": "Web Development",
            "location": "Deoghar",
            "duration": "Internship",
            "stipend": None,
            "eligibility": "Freshers",
            "skills": "HTML, CSS, JavaScript, React.js, Web Development",
            "description": "Current Web Development Intern opening listed for Deoghar with onsite internship mode.",
            "apply_link": "https://codingpara.com/career/",
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Deoghar, Jharkhand",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://codingpara.com/",
            "source_url": "https://codingpara.com/career/",
            "application_url": "https://codingpara.com/career/",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Onsite",
            "fee": None,
            "category": "Web Development",
            "provider_type": "Company",
            "contact_phone": "+91 74798 33877",
            "contact_email": "info@codingpara.com",
            "map_link": None
        }
    ]

    added = 0

    for item in opportunities:

        existing = cursor.execute(
            """
            SELECT id FROM internships
            WHERE title = ? AND company = ? AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            continue

        cursor.execute(
            """
            INSERT INTO internships (
                title,
                company,
                field,
                location,
                duration,
                stipend,
                eligibility,
                skills,
                description,
                apply_link,
                last_date,
                opportunity_type,
                address,
                area,
                city,
                official_website,
                source_url,
                application_url,
                verification_status,
                verified_at,
                mode,
                fee,
                category,
                provider_type,
                contact_phone,
                contact_email,
                map_link
            )
         VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?
)
            """,
            (
                item["title"],
                item["company"],
                item["field"],
                item["location"],
                item["duration"],
                item["stipend"],
                item["eligibility"],
                item["skills"],
                item["description"],
                item["apply_link"],
                item["last_date"],
                item["opportunity_type"],
                item["address"],
                item["area"],
                item["city"],
                item["official_website"],
                item["source_url"],
                item["application_url"],
                item["verification_status"],
                item["verified_at"],
                item["mode"],
                item["fee"],
                item["category"],
                item["provider_type"],
                item["contact_phone"],
                item["contact_email"],
                item["map_link"]
            )
        )

        added += 1

    conn.commit()
    conn.close()

    print(f"\n{added} new verified opportunities added successfully.")

# ==================================================
# DHANBAD - COMPUTER / SOFTWARE / IT PROVIDERS
# ==================================================

def add_dhanbad_opportunities():

    """
    Add verified Dhanbad internship, training and
    computer/software providers.

    Existing records are not duplicated.
    Training providers are kept as Training unless
    internship is specifically confirmed by the source.
    """

    connection = get_db_connection()

    providers = [

        # ==================================================
        # DHANBAD COMPUTER CENTRE
        # ==================================================

        {
            "title": "Computer & IT Training",
            "company": "Dhanbad Computer Centre",
            "field": "Computer Science / IT",
            "location": "Hirapur, Dhanbad",
            "duration": "Course dependent",
            "stipend": "Not applicable",
            "eligibility": "Students, job seekers and learners",
            "skills": (
                "DCA, ADCA, Tally with GST, "
                "Web Designing, DTP, Typing, "
                "Video Editing, Shorthand"
            ),
            "description": (
                "Dhanbad Computer Centre provides computer education "
                "and digital skill-development training in Dhanbad. "
                "Courses include DCA, ADCA, Tally with GST, Web Designing, "
                "DTP, Typing, Video Editing and Shorthand."
            ),
            "apply_link": "https://www.dhanbadcomputer.in/",
            "last_date": None,
            "opportunity_type": "Training",
            "address": (
                "Near Telipara Kalimandir, "
                "Hirapur, Dhanbad - 826001"
            ),
            "area": "Hirapur",
            "city": "Dhanbad",
            "official_website": "https://www.dhanbadcomputer.in/",
            "source_url": "https://www.dhanbadcomputer.in/",
            "application_url": "https://www.dhanbadcomputer.in/contact/",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline",
            "fee": "Course dependent",
            "category": "Computer / IT Training",
            "provider_type": "Training Institute",
            "contact_phone": "+91 9708511560",
            "contact_email": None,
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Dhanbad+Computer+Centre+Hirapur"
            )
        },

        # ==================================================
        # NICT ACADEMY
        # ==================================================

        {
            "title": "Computer & Programming Training",
            "company": "NICT Academy",
            "field": "Computer Science / IT",
            "location": "Hirapur, Dhanbad",
            "duration": "Course dependent",
            "stipend": "Not applicable",
            "eligibility": "Students and learners",
            "skills": (
                "DCA, ADCA, Tally, AutoCAD, "
                "Hardware, Networking, C, C++, Java, Python"
            ),
            "description": (
                "NICT Academy is an IT training centre in Hirapur, "
                "Dhanbad offering computer applications, programming, "
                "networking and other technical courses."
            ),
            "apply_link": "https://nictacademy.in/",
            "last_date": None,
            "opportunity_type": "Training",
            "address": (
                "JC Mallick Road, Behind Jagdamba Mandap, "
                "Hirapur, Dhanbad, Jharkhand - 826001"
            ),
            "area": "Hirapur",
            "city": "Dhanbad",
            "official_website": "https://nictacademy.in/",
            "source_url": "https://nictacademy.in/",
            "application_url": "https://nictacademy.in/",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline",
            "fee": "Course dependent",
            "category": "Computer / IT Training",
            "provider_type": "Training Institute",
            "contact_phone": "+91 7004225406",
            "contact_email": None,
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=NICT+Academy+Hirapur+Dhanbad"
            )
        },

        # ==================================================
        # SIMPRA COMPUTER INSTITUTE
        # ==================================================

        {
            "title": "Computer Training & Internship",
            "company": "Simpra Computer Institute",
            "field": "Computer Science / IT",
            "location": "Bank More, Dhanbad",
            "duration": "Course / Internship dependent",
            "stipend": "Not specified",
            "eligibility": "Students and computer learners",
            "skills": (
                "Computer Applications, MS Office, "
                "Tally, GST, Excel, Graphics, "
                "Video Editing, AI Prompting"
            ),
            "description": (
                "Simpra Computer Institute provides regular and "
                "professional computer courses with internship "
                "opportunities based on skills. The institute is "
                "located at Bank More, Dhanbad."
            ),
            "apply_link": "https://www.simpracomputer.com/",
            "last_date": None,
            "opportunity_type": "Training / Internship",
            "address": (
                "Room No. 337, 3rd Floor, Sri Ram Plaza, "
                "Bank More, Dhanbad, Jharkhand"
            ),
            "area": "Bank More",
            "city": "Dhanbad",
            "official_website": "https://www.simpracomputer.com/",
            "source_url": "https://www.simpracomputer.com/",
            "application_url": "https://www.simpracomputer.com/",
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline",
            "fee": "Course dependent",
            "category": "Computer / IT",
            "provider_type": "Training Institute",
            "contact_phone": "+91 8987494942",
            "contact_email": "career@simpracomputer.com",
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Simpra+Computer+Institute+Bank+More+Dhanbad"
            )
        },

        # ==================================================
        # AERONSPIRE TECHNOLOGY
        # ==================================================

        {
            "title": "Industrial Training / Internship",
            "company": "Aeronspire Technology",
            "field": "Embedded / Robotics / Automation",
            "location": "Sardar Patel Nagar, Dhanbad",
            "duration": "Programme dependent",
            "stipend": "Not specified",
            "eligibility": "Diploma / B.Tech students from engineering branches",
            "skills": (
                "Robotics, Automation, Mechatronics, "
                "Field Surveying, CNC, Embedded Systems"
            ),
            "description": (
                "Aeronspire Technology provides industrial "
                "training/internship opportunities for Diploma "
                "and B.Tech students across engineering branches."
            ),
            "apply_link": (
                "https://www.aeronspire.in/"
                "aeronspire/?p=professional-course"
            ),
            "last_date": None,
            "opportunity_type": "Training / Internship",
            "address": "Sardar Patel Nagar, Dhanbad - 826001",
            "area": "Sardar Patel Nagar",
            "city": "Dhanbad",
            "official_website": "https://www.aeronspire.in/",
            "source_url": (
                "https://www.aeronspire.in/"
                "aeronspire/?p=professional-course"
            ),
            "application_url": (
                "https://www.aeronspire.in/"
                "aeronspire/?p=professional-course"
            ),
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline",
            "fee": "Contact provider",
            "category": "Technical / Engineering",
            "provider_type": "Training / Technology Organization",
            "contact_phone": "+91 7762820555",
            "contact_email": "info@aeronspire.in",
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Aeronspire+Technology+Dhanbad"
            )
        },

        # ==================================================
        # MANAV VIKASH TRUST
        # ==================================================

        {
            "title": "IT / Design / SEO Internship",
            "company": "Manav Vikash Trust",
            "field": "IT / Design / Digital",
            "location": "Hirapur, Dhanbad",
            "duration": "Programme dependent",
            "stipend": "Not specified",
            "eligibility": "Students, volunteers and interested individuals",
            "skills": (
                "Website Designing, SEO, Research & Development, "
                "Social Media, Graphics, IT, Poster / Leaflet Design"
            ),
            "description": (
                "Manav Vikash Trust offers volunteer and internship "
                "opportunities in areas including website designing, "
                "SEO, research and development, social media, graphics "
                "and information technology."
            ),
            "apply_link": (
                "https://www.manas-india.thetechthingy.com/volunteer"
            ),
            "last_date": None,
            "opportunity_type": "Internship",
            "address": (
                "H/O-Swati Bhattacharya, Tax N Tax HE School Road, "
                "Visti Para, Hirapur, Dhanbad - 826001, Jharkhand"
            ),
            "area": "Hirapur",
            "city": "Dhanbad",
            "official_website": (
                "https://www.manas-india.thetechthingy.com/"
            ),
            "source_url": (
                "https://www.manas-india.thetechthingy.com/volunteer"
            ),
            "application_url": (
                "https://www.manas-india.thetechthingy.com/volunteer"
            ),
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline / Programme dependent",
            "fee": "Not specified",
            "category": "IT / Design / Social Sector",
            "provider_type": "Trust / NGO",
            "contact_phone": None,
            "contact_email": "trustmanavvikash@gmail.com",
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Manav+Vikash+Trust+Hirapur+Dhanbad"
            )
        },

        # ==================================================
        # WEBASHA TECHNOLOGIES
        # ==================================================

        {
            "title": "Web Development Internship",
            "company": "WebAsha Technologies",
            "field": "Web Development",
            "location": "Dhanbad",
            "duration": "6-8 Weeks",
            "stipend": "Not specified",
            "eligibility": "BCA, B.Sc IT, B.Tech, MCA and IT students",
            "skills": (
                "HTML, CSS, JavaScript, React.js, "
                "Responsive Web Development"
            ),
            "description": (
                "WebAsha Technologies lists a 2026 Summer Internship "
                "Training Program in Web Development in Dhanbad with "
                "hands-on project work and internship/project certificates."
            ),
            "apply_link": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Dhanbad, Jharkhand",
            "area": None,
            "city": "Dhanbad",
            "official_website": "https://www.webasha.com/",
            "source_url": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "application_url": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Classroom / Online / Hybrid",
            "fee": "Contact provider",
            "category": "Web Development",
            "provider_type": "IT Training / Internship Provider",
            "contact_phone": "+91 8010911256",
            "contact_email": None,
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=WebAsha+Technologies+Dhanbad"
            )
        },

        # ==================================================
        # WEBASHA - PYTHON
        # ==================================================

        {
            "title": "Python with Automation Internship",
            "company": "WebAsha Technologies",
            "field": "Python / Automation",
            "location": "Dhanbad",
            "duration": "6-8 Weeks",
            "stipend": "Not specified",
            "eligibility": "BCA, B.Sc IT, B.Tech, MCA and IT students",
            "skills": (
                "Python, Web Scraping, Automation, "
                "Selenium, PyAutoGUI, BeautifulSoup"
            ),
            "description": (
                "Summer Internship Training Program in Python with "
                "Automation covering Python programming, automation, "
                "web scraping and practical projects."
            ),
            "apply_link": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "last_date": None,
            "opportunity_type": "Internship",
            "address": "Dhanbad, Jharkhand",
            "area": None,
            "city": "Dhanbad",
            "official_website": "https://www.webasha.com/",
            "source_url": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "application_url": (
                "https://www.webasha.com/"
                "summer-internship-training-program-dhanbad"
            ),
            "verification_status": "Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Classroom / Online / Hybrid",
            "fee": "Contact provider",
            "category": "Python / Automation",
            "provider_type": "IT Training / Internship Provider",
            "contact_phone": "+91 8010911256",
            "contact_email": None,
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=WebAsha+Technologies+Dhanbad"
            )
        },

        # ==================================================
        # SOFTWARE HUB COMPUTER INSTITUTE
        # ==================================================

        {
            "title": "Computer Training",
            "company": "Software Hub Computer Institute",
            "field": "Computer Science / IT",
            "location": "Digwadih, Jorapokhar, Dhanbad",
            "duration": "Course dependent",
            "stipend": "Not applicable",
            "eligibility": "Students interested in computer education",
            "skills": (
                "Basic Computer, C Programming, C++ Programming"
            ),
            "description": (
                "Software Hub Computer Institute is a computer "
                "training centre in the Digwadih/Jorapokhar area "
                "of Dhanbad. Internship availability should be "
                "confirmed directly with the institute."
            ),
            "apply_link": "",
            "last_date": None,
            "opportunity_type": "Training",
            "address": (
                "10 Number, Digwadih, Jorapokhar, "
                "Jharkhand - 828110"
            ),
            "area": "Digwadih",
            "city": "Dhanbad",
            "official_website": "",
            "source_url": (
                "https://www.justdial.com/Dhanbad/"
                "Software-Hub-Computer-Class-Near-Shiv-Mandir-"
                "Jamadoba/9999PX326-X326-230423033610-V2M8_BZDET"
            ),
            "application_url": "",
            "verification_status": "Directory Verified",
            "verified_at": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Offline",
            "fee": "Contact provider",
            "category": "Computer Training",
            "provider_type": "Training Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": (
                "https://www.google.com/maps/search/"
                "?api=1&query=Software+Hub+Computer+Institute+Digwadih"
            )
        }
    ]

    # ==================================================
    # EXISTING DATABASE COLUMNS
    # ==================================================

    existing_columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(internships)"
        ).fetchall()
    }

    added = 0
    skipped = 0

    # ==================================================
    # INSERT PROVIDERS
    # ==================================================

    for item in providers:

        existing = connection.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            skipped += 1
            continue

        data = {
            key: value
            for key, value in item.items()
            if key in existing_columns
        }

        columns = ", ".join(data.keys())

        placeholders = ", ".join(
            ["?"] * len(data)
        )

        connection.execute(
            f"""
            INSERT INTO internships ({columns})
            VALUES ({placeholders})
            """,
            tuple(data.values())
        )

        added += 1

    connection.commit()

    # ==================================================
    # DHANBAD COUNT
    # ==================================================

    dhanbad_count = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM internships
        WHERE LOWER(city) = LOWER('Dhanbad')
        """
    ).fetchone()["total"]

    # ==================================================
    # DHANBAD AREA LIST
    # ==================================================

    areas = connection.execute(
        """
        SELECT DISTINCT area
        FROM internships
        WHERE LOWER(city) = LOWER('Dhanbad')
          AND area IS NOT NULL
          AND TRIM(area) != ''
        ORDER BY area
        """
    ).fetchall()

    connection.close()

    print()
    print("========================================")
    print(" DHANBAD OPPORTUNITIES UPDATED")
    print("========================================")

    print(
        f"{added} new Dhanbad opportunities added."
    )

    print(
        f"{skipped} Dhanbad records already existed."
    )

    print(
        f"TOTAL DHANBAD OPPORTUNITIES = {dhanbad_count}"
    )

    print()
    print("DHANBAD AREAS:")

    for row in areas:
        print(
            f"- {row['area']}"
        )
# ==================================================
# INSTITUTES DIRECTORY
# ==================================================

def create_institutes_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            institute_type TEXT NOT NULL,
            category TEXT,
            city TEXT NOT NULL,
            district TEXT,
            area TEXT,
            address TEXT,
            courses TEXT,
            official_website TEXT,
            source_url TEXT,
            phone TEXT,
            email TEXT,
            description TEXT,
            verification_status TEXT DEFAULT 'Official',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, city, institute_type)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_institutes_city
        ON institutes(city)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_institutes_type
        ON institutes(institute_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_institutes_category
        ON institutes(category)
    """)

    connection.commit()
    connection.close()

    print("INSTITUTES DIRECTORY TABLE CREATED / UPDATED")


def add_verified_jharkhand_institutes():
    """
    Add the first verified technical-education backbone of the
    Jharkhand institute directory. Missing details are left blank
    rather than invented.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    source_url = "https://www.jharkhand.gov.in/"

    institutes = [
        ("Government Polytechnic Ranchi", "Polytechnic", "Government Polytechnic",
         "Ranchi", "Ranchi", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Dhanbad", "Polytechnic", "Government Polytechnic",
         "Dhanbad", "Dhanbad", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Nirsa", "Polytechnic", "Government Polytechnic",
         "Dhanbad", "Dhanbad", "Nirsa", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic at Nirsa, Dhanbad.", "Official"),

        ("Government Polytechnic Dumka", "Polytechnic", "Government Polytechnic",
         "Dumka", "Dumka", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Adityapur", "Polytechnic", "Government Polytechnic",
         "Adityapur", "Seraikela-Kharsawan", "Adityapur", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Jainamore", "Polytechnic", "Government Polytechnic",
         "Bokaro", "Bokaro", "Jainamore", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic at Jainamore, Bokaro.", "Official"),

        ("Government Polytechnic Koderma", "Polytechnic", "Government Polytechnic",
         "Koderma", "Koderma", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Bhaga", "Polytechnic", "Government Polytechnic",
         "Dhanbad", "Dhanbad", "Bhaga", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic at Bhaga, Dhanbad.", "Official"),

        ("Government Polytechnic Latehar", "Polytechnic", "Government Polytechnic",
         "Latehar", "Latehar", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Kharsawan", "Polytechnic", "Government Polytechnic",
         "Kharsawan", "Seraikela-Kharsawan", "Kharsawan", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic at Kharsawan.", "Official"),

        ("Government Women's Polytechnic Tharpakhna", "Women's Polytechnic", "Government Women's Polytechnic",
         "Ranchi", "Ranchi", "Tharpakhna", None, "Diploma Technical Education",
         None, source_url, None, None, "Government women's polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Women's Polytechnic Gamharia", "Women's Polytechnic", "Government Women's Polytechnic",
         "Jamshedpur", "Seraikela-Kharsawan", "Gamharia", None, "Diploma Technical Education",
         None, source_url, None, None, "Government women's polytechnic at Gamharia.", "Official"),

        ("Government Women's Polytechnic Balidih", "Women's Polytechnic", "Government Women's Polytechnic",
         "Bokaro", "Bokaro", "Balidih", None, "Diploma Technical Education",
         None, source_url, None, None, "Government women's polytechnic at Balidih, Bokaro.", "Official"),

        ("Government Polytechnic Sahibganj", "Polytechnic", "Government Polytechnic",
         "Sahibganj", "Sahibganj", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Women's Polytechnic Dumka", "Women's Polytechnic", "Government Women's Polytechnic",
         "Dumka", "Dumka", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government women's polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Simdega", "Polytechnic", "Government Polytechnic",
         "Simdega", "Simdega", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Government Polytechnic Jagannathpur", "Polytechnic", "Government Polytechnic",
         "Jagannathpur", "West Singhbhum", "Jagannathpur", None, "Diploma Technical Education",
         None, source_url, None, None, "Government polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Silli Polytechnic", "Polytechnic", "PPP Mode Polytechnic",
         "Silli", "Ranchi", "Silli", None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Pakur Polytechnic", "Polytechnic", "PPP Mode Polytechnic",
         "Pakur", "Pakur", None, None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Chandil Polytechnic", "Polytechnic", "PPP Mode Polytechnic",
         "Chandil", "Seraikela-Kharsawan", "Chandil", None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Gola Polytechnic", "Polytechnic", "PPP Mode Polytechnic",
         "Gola", "Ramgarh", "Gola", None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Beharagora Polytechnic College", "Polytechnic", "PPP Mode Polytechnic",
         "Beharagora", "East Singhbhum", "Beharagora", None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Garhwa Polytechnic", "Polytechnic", "PPP Mode Polytechnic",
         "Garhwa", "Garhwa", None, None, "Diploma Technical Education",
         None, source_url, None, None, "PPP mode polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Institute of Science & Management, Pundag", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", "Pundag", None, "Diploma Technical Education",
         None, source_url, None, None, "Private technical institute listed in the Jharkhand technical education directory.", "Official"),

        ("Al-Kabir Polytechnic", "Polytechnic", "Private Polytechnic",
         "Jamshedpur", "East Singhbhum", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("K.K. Polytechnic, Govindpur", "Polytechnic", "Private Polytechnic",
         "Dhanbad", "Dhanbad", "Govindpur", None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("K.K. College of Engineering & Management", "Engineering College", "Private Technical Institute",
         "Dhanbad", "Dhanbad", "Govindpur", None, "Engineering & Technical Education",
         None, source_url, None, None, "Technical institute listed in the Jharkhand technical education directory.", "Official"),

        ("Centre for Bio-Informatics, Hinoo", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", "Hinoo", None, "Diploma Technical Education",
         None, source_url, None, None, "Private technical institute listed in the Jharkhand technical education directory.", "Official"),

        ("Vidya Memorial Institute of Technology", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", "Tupudana", None, "Diploma Technical Education",
         None, source_url, None, None, "Private technical institute listed in the Jharkhand technical education directory.", "Official"),

        ("BITT Polytechnic", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Sarojini Institute of Technology", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", "Tata Ranchi Road", None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Ramgovind Polytechnic Institute", "Polytechnic", "Private Polytechnic",
         "Koderma", "Koderma", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Khandoli Institute of Technology", "Polytechnic", "Private Polytechnic",
         "Giridih", "Giridih", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Cambridge Institute of Polytechnic", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", "Angara", None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Pemiya Rishikesh Institute of Technology", "Polytechnic", "Private Polytechnic",
         "Dhanbad", "Dhanbad", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Subhash Institute of Technology", "Polytechnic", "Private Polytechnic",
         "Giridih", "Giridih", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("RTC Institute of Technology", "Engineering & Polytechnic", "Private Technical Institute",
         "Ranchi", "Ranchi", None, None, "Engineering & Diploma Technical Education",
         None, source_url, None, None, "Technical institute listed in the Jharkhand technical education directory.", "Official"),

        ("Girija Institute of Polytechnic", "Polytechnic", "Private Polytechnic",
         "Ramgarh", "Ramgarh", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Xavier Institute of Polytechnic and Technology", "Polytechnic", "Private Polytechnic",
         "Ranchi", "Ranchi", None, None, "Diploma Technical Education",
         None, source_url, None, None, "Private polytechnic listed in the Jharkhand technical education directory.", "Official"),

        ("Nilaai Educational Trusts Group of Institution", "Technical Institute", "Private Technical Institute",
         "Ranchi", "Ranchi", None, None, "Technical Education",
         None, source_url, None, None, "Technical institute listed in the Jharkhand technical education directory.", "Official"),
    ]

    added = 0

    for item in institutes:
        cursor.execute("""
            INSERT OR IGNORE INTO institutes (
                name, institute_type, category, city, district, area,
                address, courses, official_website, source_url,
                phone, email, description, verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

        if cursor.rowcount > 0:
            added += 1

    connection.commit()

    total = cursor.execute(
        "SELECT COUNT(*) AS total FROM institutes"
    ).fetchone()["total"]

    city_data = cursor.execute("""
        SELECT city, COUNT(*) AS total
        FROM institutes
        GROUP BY city
        ORDER BY city
    """).fetchall()

    connection.close()

    print()
    print("========================================")
    print(" INSTITUTE DIRECTORY")
    print("========================================")
    print(f"{added} new institutes added successfully.")
    print(f"TOTAL INSTITUTES = {total}")

    for row in city_data:
        print(f"{row['city']} = {row['total']}")


def get_institute_count():
    connection = get_db_connection()
    total = connection.execute(
        "SELECT COUNT(*) AS total FROM institutes"
    ).fetchone()["total"]
    connection.close()
    return total

# ==================================================
# ADDITIONAL VERIFIED INTERNSHIP CENTRES
# ==================================================

def add_more_real_opportunities():

    conn = get_db_connection()

    today = datetime.now().strftime("%Y-%m-%d")

    opportunities = [

        # ==================================================
        # JAMSHEDPUR - NIT JSR / DHTE
        # ==================================================

        {
            "title": "Industrial Training & Internship Programme",
            "company": "NIT Jamshedpur - DHTE Jharkhand",
            "field": "Industrial Training / Technical Skills",
            "location": "Jamshedpur",
            "duration": "6 Weeks",
            "eligibility": "Students of Government Polytechnic and Government Women's Polytechnic institutions in Jharkhand",
            "skills": "Technical Training, Industrial Skills, Practical Learning",
            "description": "Structured industrial training and internship programme hosted by NIT Jamshedpur under the DHTE Jharkhand initiative.",
            "apply_link": "https://www.nitjsrintern.in/",
            "last_date": "Check official portal for current batch",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIT Jamshedpur, Jharkhand - 831014",
            "area": None,
            "city": "Jamshedpur",
            "official_website": "https://www.nitjsrintern.in/",
            "source_url": "https://www.nitjsrintern.in/",
            "application_url": "https://www.nitjsrintern.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Residential / Onsite",
            "fee": "Check official portal",
            "category": "Industrial Training",
            "provider_type": "Government / Institute",
            "contact_phone": None,
            "contact_email": "internship@nitjsr.ac.in",
            "map_link": None
        },

        # ==================================================
        # JAMSHEDPUR - GLOBUS LABS
        # ==================================================

        {
            "title": "Technology Internship Programme",
            "company": "Globus Labs",
            "field": "Web Development / Android / SAP / Java",
            "location": "Jamshedpur",
            "duration": "Varies by track",
            "eligibility": "Students and learners interested in technology internships",
            "skills": "SAP Business One, Android, Web Development, Java, Oracle",
            "description": "Structured internship tracks with live project exposure and mentoring. Jamshedpur is listed among available internship locations.",
            "apply_link": "https://globuslabs.com/career.html",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": None,
            "area": None,
            "city": "Jamshedpur",
            "official_website": "https://globuslabs.com/",
            "source_url": "https://globuslabs.com/career.html",
            "application_url": "https://globuslabs.com/career.html",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Software Company",
            "contact_phone": None,
            "contact_email": "hr@globuslabs.com",
            "map_link": None
        },

        # ==================================================
        # RANCHI - GRAPHIX MEDIA
        # ==================================================

        {
            "title": "Software & Digital Internship",
            "company": "Graphix Media",
            "field": "Web / App / Software / Design / Digital Marketing",
            "location": "Ranchi",
            "duration": "6 Weeks to 6 Months",
            "eligibility": "B.Tech, BCA, MCA, Diploma CS/IT students, graduates and freshers",
            "skills": "HTML, CSS, JavaScript, React, PHP, Laravel, Android, UI/UX, SEO",
            "description": "Structured internship programme with live project exposure, mentorship and practical software, design and digital marketing work.",
            "apply_link": "https://graphixmedia.net/service-internship",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "401, HR Complex, Near Hotel Pearl Regency, Kadru Main Road, Ranchi - 834002, Jharkhand",
            "area": "Kadru",
            "city": "Ranchi",
            "official_website": "https://www.graphixmedia.net/",
            "source_url": "https://graphixmedia.net/service-internship",
            "application_url": "https://graphixmedia.net/service-internship",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite / Remote",
            "fee": None,
            "category": "IT & Digital",
            "provider_type": "Software Company",
            "contact_phone": "+91 9334450056",
            "contact_email": "contact@graphixmedia.net",
            "map_link": None
        },

        # ==================================================
        # RANCHI - SUDHA SOFTWARE
        # ==================================================

        {
            "title": "50-Day Industry Internship",
            "company": "Sudha Software Solutions Private Limited",
            "field": "Software / AI / Digital Marketing",
            "location": "Ranchi",
            "duration": "50 Days",
            "eligibility": "BCA, B.Tech, MCA, Diploma, BBA, MBA, B.Sc CS/IT and related students",
            "skills": "Frontend, Backend, AI Automation, Full Stack, UI/UX, Digital Marketing",
            "description": "Remote industry internship programme with structured mentorship, live project work and multiple technology tracks.",
            "apply_link": "https://sudhasoftwaresolutions.com/internships",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "01 Ground Floor, BOI Zonal Office Building, Pragti Path, Makchund Toli, Chutia, Ranchi - 834001",
            "area": "Chutia",
            "city": "Ranchi",
            "official_website": "https://sudhasoftwaresolutions.com/",
            "source_url": "https://sudhasoftwaresolutions.com/internships",
            "application_url": "https://sudhasoftwaresolutions.com/internships",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Remote",
            "fee": "₹5,000 all-inclusive",
            "category": "IT & Software",
            "provider_type": "Software Company",
            "contact_phone": "+91 9608886504",
            "contact_email": "contact@sudhasoftwaresolutions.com",
            "map_link": None
        },

        # ==================================================
        # DHANBAD - IIT(ISM)
        # ==================================================

        {
            "title": "Summer Research Internship Scheme",
            "company": "IIT (ISM) Dhanbad",
            "field": "Research / Technical",
            "location": "Dhanbad",
            "duration": "Up to 2 Months",
            "eligibility": "Undergraduate and Postgraduate students as per institute guidelines",
            "skills": "Research, Technical Projects, Department-specific Skills",
            "description": "IIT(ISM) Dhanbad research internship programme involving faculty-guided project work and academic review.",
            "apply_link": "https://people.iitism.ac.in/~research/SRIP.php",
            "last_date": "2026 cycle closed; check official website for next cycle",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "IIT(ISM) Dhanbad, Dhanbad - 826004",
            "area": None,
            "city": "Dhanbad",
            "official_website": "https://www.iitism.ac.in/",
            "source_url": "https://people.iitism.ac.in/~research/SRIP.php",
            "application_url": "https://people.iitism.ac.in/~research/SRIP.php",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "On Campus",
            "fee": "As per institute guidelines",
            "category": "Research",
            "provider_type": "Government Institute",
            "contact_phone": "+91 326 2235203",
            "contact_email": "drnd@iitism.ac.in",
            "map_link": None
        },

        # ==================================================
        # DHANBAD - BIT SINDRI
        # ==================================================

        {
            "title": "Summer Internship - CSE / IT",
            "company": "BIT Sindri",
            "field": "Computer Science & IT",
            "location": "Dhanbad",
            "duration": "Summer Programme",
            "eligibility": "Technical students as per department programme guidelines",
            "skills": "Programming, Machine Learning, Data, Communication Systems",
            "description": "Department-based summer internship programme conducted by BIT Sindri with technical project and academic learning components.",
            "apply_link": "https://www.bitsindri.ac.in/",
            "last_date": "2026 cycle closed; check official website for next programme",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "BIT Sindri, P.O. Sindri Institute, Dhanbad - 828123, Jharkhand",
            "area": "Sindri",
            "city": "Dhanbad",
            "official_website": "https://www.bitsindri.ac.in/",
            "source_url": "https://www.bitsindri.ac.in/",
            "application_url": "https://www.bitsindri.ac.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "On Campus",
            "fee": "Programme dependent",
            "category": "Engineering / IT",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # DEOGHAR - WIPENEX
        # ==================================================

        {
            "title": "IT Internship & Industrial Training",
            "company": "Wipenex",
            "field": "IT / Software Development",
            "location": "Deoghar",
            "duration": "2-3 Months / 6 Months",
            "eligibility": "B.Tech, BCA, MCA, M.Tech and IT-related students",
            "skills": "Software Development, Database, Web Technologies",
            "description": "IT training centre offering internship and industrial training programmes with live project exposure and mentorship.",
            "apply_link": "https://wipenex.in/deoghar/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Deoghar, Jharkhand",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/deoghar/it-training",
            "application_url": "https://wipenex.in/deoghar/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "IT & Software",
            "provider_type": "Training / IT Company",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # DEOGHAR - WHITEDAVID
        # ==================================================

        {
            "title": "Technology Internship Programme",
            "company": "WhiteDavid23",
            "field": "IT / Cyber Security / Software",
            "location": "Deoghar",
            "duration": "Programme dependent",
            "eligibility": "Students and learners interested in technology",
            "skills": "Cyber Security, Python, AI, Data Science, Networking",
            "description": "Technology-focused internship and training programme based in Deoghar with practical and industry-oriented learning.",
            "apply_link": "https://internship.whitedavid23.org/",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Deoghar, Jharkhand",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://internship.whitedavid23.org/",
            "source_url": "https://internship.whitedavid23.org/",
            "application_url": "https://internship.whitedavid23.org/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite / Remote",
            "fee": "Check official website",
            "category": "IT & Cyber Security",
            "provider_type": "Training / Technology",
            "contact_phone": "+91 8757219471",
            "contact_email": "whitedavidinstitute@gmail.com",
            "map_link": None
        },

        # ==================================================
        # HAZARIBAGH - WIPENEX
        # ==================================================

        {
            "title": "IT Internship & Industrial Training",
            "company": "Wipenex",
            "field": "IT / Software Development",
            "location": "Hazaribagh",
            "duration": "2-3 Months / 6 Months",
            "eligibility": "B.Tech, BCA, MCA, M.Tech and IT-related students",
            "skills": "Software Development, Database, Web Technologies",
            "description": "IT training and internship programme in Hazaribagh with live project work, mentorship and industrial training options.",
            "apply_link": "https://wipenex.in/hazaribagh/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Hazaribagh, Jharkhand",
            "area": None,
            "city": "Hazaribagh",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/hazaribagh/it-training",
            "application_url": "https://wipenex.in/hazaribagh/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "IT & Software",
            "provider_type": "Training / IT Company",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # HAZARIBAGH - KESHRI TECH
        # ==================================================

        {
            "title": "IT Internship & Career Training",
            "company": "Keshri Tech Solution",
            "field": "IT / Software",
            "location": "Hazaribagh",
            "duration": "Programme dependent",
            "eligibility": "B.Tech, BCA, B.Sc IT, Diploma and graduates",
            "skills": "Technical Training, Practical Projects, Interview Preparation",
            "description": "Career-oriented technology programme with practical internship exposure, mentorship and placement support.",
            "apply_link": "https://www.keshritechsolution.in/career",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Hazaribagh, Jharkhand",
            "area": None,
            "city": "Hazaribagh",
            "official_website": "https://www.keshritechsolution.in/",
            "source_url": "https://www.keshritechsolution.in/career",
            "application_url": "https://www.keshritechsolution.in/career",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Programme dependent",
            "fee": "Check official website",
            "category": "IT & Software",
            "provider_type": "Technology / Training",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # BOKARO - SAIL / BOKARO STEEL PLANT
        # ==================================================

        {
            "title": "Vocational Training / Internship Programme",
            "company": "SAIL - Bokaro Steel Plant",
            "field": "Industrial / Technical / Management",
            "location": "Bokaro",
            "duration": "2 to 24 Weeks depending on programme",
            "eligibility": "Engineering, Polytechnic, B.Com, B.Sc, BA, BBA, BCA and other eligible students as per scheme",
            "skills": "Industrial Exposure, Technical Learning, Safety, Departmental Training",
            "description": "Bokaro Steel Plant vocational training programme providing industrial exposure and project-based training for eligible students.",
            "apply_link": "https://vt.sailbsl.in/",
            "last_date": "Check official training portal",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "Bokaro Steel Plant, Bokaro, Jharkhand",
            "area": None,
            "city": "Bokaro",
            "official_website": "https://www.sail.co.in/",
            "source_url": "https://vt.sailbsl.in/",
            "application_url": "https://vt.sailbsl.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "As per training scheme",
            "category": "Industrial Training",
            "provider_type": "PSU / Steel Plant",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # BOKARO - CDIT INFOTECH
        # ==================================================

        {
            "title": "Website Development & IoT Internship",
            "company": "CDIT Infotech Pvt. Ltd.",
            "field": "Web Development / IoT",
            "location": "Bokaro",
            "duration": "45 Days",
            "eligibility": "Students and learners interested in Web Development and IoT",
            "skills": "Full Stack Web Development, IoT, Practical Projects",
            "description": "45-day internship programme covering website development and IoT with practical project experience and certificate.",
            "apply_link": "https://www.cdit.in/courses.aspx",
            "last_date": "Check official website for next batch",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "GE-15, City Centre, Sector-4, Bokaro Steel City, Jharkhand - 827004",
            "area": "Sector-4",
            "city": "Bokaro",
            "official_website": "https://www.cdit.in/",
            "source_url": "https://www.cdit.in/courses.aspx",
            "application_url": "https://www.cdit.in/courses.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Registration fee applicable",
            "category": "IT & IoT",
            "provider_type": "IT / Training Company",
            "contact_phone": "+91 9801360327",
            "contact_email": "info@cdit.in",
            "map_link": None
        }
    ]

    added = 0

    for item in opportunities:

        existing = conn.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            continue

        columns = ", ".join(item.keys())

        placeholders = ", ".join(
            ["?"] * len(item)
        )

        values = tuple(
            item.values()
        )

        conn.execute(
            f"""
            INSERT INTO internships (
                {columns}
            )
            VALUES (
                {placeholders}
            )
            """,
            values
        )

        added += 1

    conn.commit()
    conn.close()

    print()
    print(
        f"{added} additional verified opportunities "
        f"added successfully."
    )

    # ==================================================
# MORE VERIFIED OPPORTUNITIES - BATCH 2
# ==================================================

def add_more_verified_opportunities_batch_2():

    conn = get_db_connection()

    today = datetime.now().strftime("%Y-%m-%d")

    opportunities = [

        # ==================================================
        # JAMSHEDPUR - NIT JSR / DHTE
        # ==================================================

        {
            "title": "Industrial Training Programme",
            "company": "NIT Jamshedpur - DHTE Jharkhand",
            "field": "Industrial Training / Technical Skills",
            "location": "Jamshedpur",
            "duration": "6 Weeks",
            "eligibility": "Eligible students under the NIT Jamshedpur - DHTE industrial training programme",
            "skills": "Technical Training, Industrial Skills, Practical Learning",
            "description": "Structured industrial training programme conducted at NIT Jamshedpur under the DHTE Jharkhand initiative.",
            "apply_link": "https://www.nitjsrintern.in/",
            "last_date": "Check official portal",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "NIT Jamshedpur, Adityapur, Jamshedpur, Jharkhand - 831014",
            "area": "Adityapur",
            "city": "Jamshedpur",
            "official_website": "https://www.nitjsrintern.in/",
            "source_url": "https://www.nitjsrintern.in/",
            "application_url": "https://www.nitjsrintern.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official portal",
            "category": "Industrial Training",
            "provider_type": "Institute / Government Programme",
            "contact_phone": None,
            "contact_email": "internship@nitjsr.ac.in",
            "map_link": None
        },

        # ==================================================
        # JAMSHEDPUR - GLOBUS
        # ==================================================

        {
            "title": "Android Development Internship",
            "company": "Globus Labs",
            "field": "Android Development",
            "location": "Jamshedpur",
            "duration": "Programme dependent",
            "eligibility": "Students interested in Android development",
            "skills": "Android, Jetpack Compose, Mobile App Development",
            "description": "Structured Android development internship with live project exposure and industry mentorship.",
            "apply_link": "https://globuslabs.com/career.html",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": None,
            "area": None,
            "city": "Jamshedpur",
            "official_website": "https://globuslabs.com/",
            "source_url": "https://globuslabs.com/career.html",
            "application_url": "https://globuslabs.com/career.html",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": None,
            "category": "Mobile Development",
            "provider_type": "Software Company",
            "contact_phone": None,
            "contact_email": "hr@globuslabs.com",
            "map_link": None
        },

        {
            "title": "Java / Oracle Internship",
            "company": "Globus Labs",
            "field": "Java / Oracle",
            "location": "Jamshedpur",
            "duration": "Programme dependent",
            "eligibility": "Students interested in Java and database technologies",
            "skills": "Java, Oracle, Database Development",
            "description": "Technology internship track offering training and exposure to live projects in Java and Oracle.",
            "apply_link": "https://globuslabs.com/career.html",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": None,
            "area": None,
            "city": "Jamshedpur",
            "official_website": "https://globuslabs.com/",
            "source_url": "https://globuslabs.com/career.html",
            "application_url": "https://globuslabs.com/career.html",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": None,
            "category": "IT & Software",
            "provider_type": "Software Company",
            "contact_phone": None,
            "contact_email": "hr@globuslabs.com",
            "map_link": None
        },

        # ==================================================
        # RANCHI - NIELIT
        # ==================================================

        {
            "title": "Internet of Things Internship",
            "company": "NIELIT Ranchi",
            "field": "Internet of Things (IoT)",
            "location": "Ranchi",
            "duration": "1 Month",
            "eligibility": "Students eligible for College / Summer Internship programmes",
            "skills": "IoT, Sensors, Embedded Systems, Networking",
            "description": "College / Summer Internship on Internet of Things listed by NIELIT Ranchi.",
            "apply_link": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "last_date": "Check NIELIT Ranchi course list",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIELIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://ranchi.nielit.edu.in/",
            "source_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "application_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Check official course listing",
            "category": "IoT",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Data Analytics Using Python Internship",
            "company": "NIELIT Ranchi",
            "field": "Data Analytics",
            "location": "Ranchi",
            "duration": "1 Month",
            "eligibility": "Students eligible for College / Summer Internship programmes",
            "skills": "Python, Data Analytics, Data Visualization",
            "description": "College / Summer Internship on Data Analytics Using Python listed by NIELIT Ranchi.",
            "apply_link": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "last_date": "Check NIELIT Ranchi course list",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIELIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://ranchi.nielit.edu.in/",
            "source_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "application_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Check official course listing",
            "category": "Data Analytics",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "AI Using Python Internship",
            "company": "NIELIT Ranchi",
            "field": "Artificial Intelligence",
            "location": "Ranchi",
            "duration": "1 Month",
            "eligibility": "Students eligible for College / Summer Internship programmes",
            "skills": "Python, Artificial Intelligence, Machine Learning Basics",
            "description": "College / Summer Internship on AI Using Python listed by NIELIT Ranchi.",
            "apply_link": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "last_date": "Check NIELIT Ranchi course list",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIELIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://ranchi.nielit.edu.in/",
            "source_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "application_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Check official course listing",
            "category": "AI & ML",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Cyber Security and Ethical Hacking Internship",
            "company": "NIELIT Ranchi",
            "field": "Cyber Security",
            "location": "Ranchi",
            "duration": "1 Month",
            "eligibility": "Students eligible for College / Summer Internship programmes",
            "skills": "Cyber Security, Ethical Hacking, Network Security",
            "description": "College / Summer Internship on Cyber Security and Ethical Hacking listed by NIELIT Ranchi.",
            "apply_link": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "last_date": "Check NIELIT Ranchi course list",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIELIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://ranchi.nielit.edu.in/",
            "source_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "application_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Check official course listing",
            "category": "Cyber Security",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Web Designing Internship",
            "company": "NIELIT Ranchi",
            "field": "Web Designing",
            "location": "Ranchi",
            "duration": "1 Month",
            "eligibility": "Students eligible for College / Summer Internship programmes",
            "skills": "HTML, CSS, Web Designing, UI Basics",
            "description": "College / Summer Internship on Web Designing listed by NIELIT Ranchi.",
            "apply_link": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "last_date": "Check NIELIT Ranchi course list",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "NIELIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://ranchi.nielit.edu.in/",
            "source_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "application_url": "https://ranchi.nielit.edu.in/training/student/centre_courses_list.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Check official course listing",
            "category": "Web Development",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # RANCHI - IIIT RANCHI
        # ==================================================

        {
            "title": "Summer Internship Programme 2026",
            "company": "Indian Institute of Information Technology Ranchi",
            "field": "Computer Science & Information Technology",
            "location": "Ranchi",
            "duration": "Summer Internship",
            "eligibility": "First-year, second-year and third-year B.Tech / B.E. students from institutions other than IIIT Ranchi",
            "skills": "Computer Science, Information Technology, Research / Project Work",
            "description": "Summer Internship Programme 2026 organized by IIIT Ranchi.",
            "apply_link": "https://iiitranchi.ac.in/",
            "last_date": "2026 cycle notice; check official website for next programme",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "IIIT Ranchi, Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://iiitranchi.ac.in/",
            "source_url": "https://iiitranchi.ac.in/",
            "application_url": "https://iiitranchi.ac.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Institute / Programme dependent",
            "fee": "Check official notice",
            "category": "Computer Science & IT",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # DHANBAD - IIT ISM
        # ==================================================

        {
            "title": "Summer Research Internship Programme",
            "company": "IIT (ISM) Dhanbad",
            "field": "Research / Technical",
            "location": "Dhanbad",
            "duration": "8 Weeks",
            "eligibility": "Eligible students as per SRIP guidelines",
            "skills": "Research, Technical Project Work, Presentation",
            "description": "Summer Research Internship Programme at IIT (ISM) Dhanbad with faculty-guided research and project work.",
            "apply_link": "https://people.iitism.ac.in/~research/SRIP.php",
            "last_date": "Check official SRIP notice",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "IIT (ISM) Dhanbad, Dhanbad - 826004, Jharkhand",
            "area": None,
            "city": "Dhanbad",
            "official_website": "https://www.iitism.ac.in/",
            "source_url": "https://people.iitism.ac.in/~research/SRIP.php",
            "application_url": "https://people.iitism.ac.in/~research/SRIP.php",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "On Campus",
            "fee": "As per official notice",
            "category": "Research",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # DHANBAD - BIT SINDRI
        # ==================================================

        {
            "title": "CSE & IT Summer Internship Programme",
            "company": "BIT Sindri",
            "field": "Computer Science & IT",
            "location": "Dhanbad",
            "duration": "Summer Programme",
            "eligibility": "Eligible technical students as per BIT Sindri programme notice",
            "skills": "Programming, Computer Science, IT Project Work",
            "description": "Summer Internship Programme organized by the Department of CSE & IT, BIT Sindri.",
            "apply_link": "https://www.bitsindri.ac.in/notice-for-summer-internship-programme-2026-organized-by-department-of-cse-it/",
            "last_date": "2026 cycle completed; check official website for next programme",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "BIT Sindri, Dhanbad - 828123, Jharkhand",
            "area": "Sindri",
            "city": "Dhanbad",
            "official_website": "https://www.bitsindri.ac.in/",
            "source_url": "https://www.bitsindri.ac.in/notice-for-summer-internship-programme-2026-organized-by-department-of-cse-it/",
            "application_url": "https://www.bitsindri.ac.in/notice-for-summer-internship-programme-2026-organized-by-department-of-cse-it/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "On Campus",
            "fee": "Check official notice",
            "category": "Engineering / IT",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        {
            "title": "Civil Engineering Summer Internship",
            "company": "BIT Sindri",
            "field": "Civil Engineering",
            "location": "Dhanbad",
            "duration": "1 June - 15 July 2026",
            "eligibility": "Diploma and B.E / B.Tech students as mentioned in programme brochure",
            "skills": "Civil Engineering, Hydrology, AutoCAD, Transportation, Geotechnical Engineering",
            "description": "Civil Engineering Summer Internship Programme covering technical topics and hands-on engineering work.",
            "apply_link": "https://www.bitsindri.ac.in/",
            "last_date": "2026 cycle completed; check official website for next programme",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "BIT Sindri, Dhanbad - 828123, Jharkhand",
            "area": "Sindri",
            "city": "Dhanbad",
            "official_website": "https://www.bitsindri.ac.in/",
            "source_url": "https://www.bitsindri.ac.in/",
            "application_url": "https://www.bitsindri.ac.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "On Campus",
            "fee": "₹1,000 in 2026 brochure",
            "category": "Civil Engineering",
            "provider_type": "Government Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # BOKARO - CDIT
        # ==================================================

        {
            "title": "Full Stack Web Development Internship",
            "company": "CDIT Infotech Pvt. Ltd.",
            "field": "Full Stack Web Development",
            "location": "Bokaro",
            "duration": "45 Days",
            "eligibility": "Students interested in Web Development",
            "skills": "Frontend, Backend, Full Stack Development",
            "description": "45-day hands-on internship programme with website development, real project experience and mentorship.",
            "apply_link": "https://www.cdit.in/courses.aspx",
            "last_date": "Check official website for next batch",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "GE-15, City Centre, Sector-4, Bokaro Steel City, Jharkhand - 827004",
            "area": "Sector-4",
            "city": "Bokaro",
            "official_website": "https://www.cdit.in/",
            "source_url": "https://www.cdit.in/courses.aspx",
            "application_url": "https://www.cdit.in/courses.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Registration fee applicable",
            "category": "IT & Software",
            "provider_type": "IT / Training Company",
            "contact_phone": "+91 9801360327",
            "contact_email": "info@cdit.in",
            "map_link": None
        },

        {
            "title": "Internet of Things Internship",
            "company": "CDIT Infotech Pvt. Ltd.",
            "field": "Internet of Things",
            "location": "Bokaro",
            "duration": "45 Days",
            "eligibility": "Students interested in IoT and technology",
            "skills": "IoT, Electronics, Sensors, Practical Projects",
            "description": "45-day internship programme covering Internet of Things with hands-on project experience.",
            "apply_link": "https://www.cdit.in/courses.aspx",
            "last_date": "Check official website for next batch",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "GE-15, City Centre, Sector-4, Bokaro Steel City, Jharkhand - 827004",
            "area": "Sector-4",
            "city": "Bokaro",
            "official_website": "https://www.cdit.in/",
            "source_url": "https://www.cdit.in/courses.aspx",
            "application_url": "https://www.cdit.in/courses.aspx",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Registration fee applicable",
            "category": "IoT",
            "provider_type": "IT / Training Company",
            "contact_phone": "+91 9801360327",
            "contact_email": "info@cdit.in",
            "map_link": None
        },

        # ==================================================
        # BOKARO - SAIL
        # ==================================================

        {
            "title": "Technical Skill Development Programme",
            "company": "SAIL - Bokaro Steel Plant",
            "field": "Industrial / Technical Skills",
            "location": "Bokaro",
            "duration": "Programme dependent",
            "eligibility": "Eligible local youth / trainees under applicable skill development programmes",
            "skills": "Electrician, Welder, Fitter, Technical Skills",
            "description": "Bokaro Steel Plant supports technical skill development and ITI-oriented training programmes for eligible youth.",
            "apply_link": "https://sail.co.in/en/plants/bokaro-steel-plant/community",
            "last_date": "Check official SAIL / Bokaro Steel Plant notices",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "Bokaro Steel Plant, Bokaro Steel City, Jharkhand",
            "area": None,
            "city": "Bokaro",
            "official_website": "https://www.sail.co.in/",
            "source_url": "https://sail.co.in/en/plants/bokaro-steel-plant/community",
            "application_url": "https://sail.co.in/en/plants/bokaro-steel-plant/community",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Programme dependent",
            "category": "Industrial Training",
            "provider_type": "PSU / Steel Plant",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # HAZARIBAGH - WIPENEX
        # ==================================================

        {
            "title": "Python Programming Internship Track",
            "company": "Wipenex",
            "field": "Python / Software Development",
            "location": "Hazaribagh",
            "duration": "Programme dependent",
            "eligibility": "IT-related students and learners",
            "skills": "Python, Django, Flask, Data Analysis, Automation",
            "description": "Python-focused practical learning track available from Wipenex Hazaribagh with software development exposure.",
            "apply_link": "https://wipenex.in/hazaribagh/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "Hazaribagh, Jharkhand",
            "area": None,
            "city": "Hazaribagh",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/hazaribagh/it-training",
            "application_url": "https://wipenex.in/hazaribagh/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "IT & Software",
            "provider_type": "IT / Training Company",
            "contact_phone": "+91 9431323903",
            "contact_email": "info@wipenex.in",
            "map_link": None
        },

        {
            "title": "Machine Learning & AI Training Track",
            "company": "Wipenex",
            "field": "AI / Machine Learning",
            "location": "Hazaribagh",
            "duration": "6 Months",
            "eligibility": "Students and learners interested in AI / ML",
            "skills": "Machine Learning, Deep Learning, Neural Networks",
            "description": "Advanced AI and Machine Learning training track listed by Wipenex Hazaribagh.",
            "apply_link": "https://wipenex.in/hazaribagh/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "Hazaribagh, Jharkhand",
            "area": None,
            "city": "Hazaribagh",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/hazaribagh/it-training",
            "application_url": "https://wipenex.in/hazaribagh/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "AI & ML",
            "provider_type": "IT / Training Company",
            "contact_phone": "+91 9431323903",
            "contact_email": "info@wipenex.in",
            "map_link": None
        },

        # ==================================================
        # HAZARIBAGH - AISECT UNIVERSITY
        # ==================================================

        {
            "title": "University Internship Programme",
            "company": "AISECT University Jharkhand",
            "field": "Technical / Career Development",
            "location": "Hazaribagh",
            "duration": "Programme dependent",
            "eligibility": "Eligible university students as per internship programme",
            "skills": "Technical Skills, Professional Skills, Industry Exposure",
            "description": "AISECT University Hazaribagh facilitates internships as part of its Training and Placement activities.",
            "apply_link": "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "last_date": "Check official university programme",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Village Jonhiya, P.O. Mahesra, P.S. Daru, Hazaribag - 825301, Jharkhand",
            "area": "Daru / Mahesra",
            "city": "Hazaribagh",
            "official_website": "https://aisectuniversityjharkhand.ac.in/",
            "source_url": "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "application_url": "https://aisectuniversityjharkhand.ac.in/TrainingandInternships",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Programme dependent",
            "fee": "Programme dependent",
            "category": "Education & Career",
            "provider_type": "University",
            "contact_phone": "8252299990",
            "contact_email": "info@aisectuniversityjharkhand.ac.in",
            "map_link": None
        },

        # ==================================================
        # DEOGHAR - WIPENEX
        # ==================================================

        {
            "title": "Summer Internship Programme",
            "company": "Wipenex",
            "field": "IT / Software Development",
            "location": "Deoghar",
            "duration": "2-3 Months",
            "eligibility": "B.Tech, BCA, MCA, M.Tech and other IT-related students",
            "skills": "Software Development, Web Technologies, Database",
            "description": "Summer internship programme with live projects, dedicated mentoring and practical IT experience.",
            "apply_link": "https://wipenex.in/deoghar/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Deoghar, Jharkhand",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/deoghar/it-training",
            "application_url": "https://wipenex.in/deoghar/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "IT & Software",
            "provider_type": "IT / Training Company",
            "contact_phone": None,
            "contact_email": "info@wipenex.in",
            "map_link": None
        },

        {
            "title": "Industrial Training Programme",
            "company": "Wipenex",
            "field": "Industrial Training / IT",
            "location": "Deoghar",
            "duration": "6 Months",
            "eligibility": "Final-year IT-related students and eligible learners",
            "skills": "Software Development, Live Projects, Industry Skills",
            "description": "Six-month industrial training programme with multiple live projects, industry mentorship and placement assistance.",
            "apply_link": "https://wipenex.in/deoghar/it-training",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "Deoghar, Jharkhand",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://wipenex.in/",
            "source_url": "https://wipenex.in/deoghar/it-training",
            "application_url": "https://wipenex.in/deoghar/it-training",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official website",
            "category": "Industrial Training",
            "provider_type": "IT / Training Company",
            "contact_phone": None,
            "contact_email": "info@wipenex.in",
            "map_link": None
        }
    ]

    added = 0

    for item in opportunities:

        existing = conn.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            continue

        columns = ", ".join(item.keys())

        placeholders = ", ".join(
            ["?"] * len(item)
        )

        conn.execute(
            f"""
            INSERT INTO internships (
                {columns}
            )
            VALUES (
                {placeholders}
            )
            """,
            tuple(item.values())
        )

        added += 1

    conn.commit()
    conn.close()

    print()
    print(
        f"{added} additional verified opportunities "
        f"from batch 2 added successfully."
    )

    # ==================================================
# ADDITIONAL UNIQUE CENTRES / PROGRAMMES - BATCH 3
# ==================================================

def add_unique_centres_batch_3():

    conn = get_db_connection()

    today = datetime.now().strftime("%Y-%m-%d")

    opportunities = [

        # ==================================================
        # JAMSHEDPUR - SOLUTION
        # ==================================================

        {
            "title": "Summer Internship Programme",
            "company": "SOLUTION - A Human Development Society",
            "field": "Social Development / Skill Development",
            "location": "Jamshedpur",
            "duration": "May - June 2026",
            "stipend": "Not specified",
            "eligibility": "Passionate and socially driven students",
            "skills": "Community Development, Skill Development, Research, Social Work",
            "description": "Summer Internship Programme for students interested in social development, community work, skill development and related activities.",
            "apply_link": "https://solution.org.in/",
            "last_date": "2026 programme announced for May-June; check official website for next cycle",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "180 Bhuiyadih, In front of Jusco Pumping Station, Jamshedpur - 831009",
            "area": "Bhuiyadih",
            "city": "Jamshedpur",
            "official_website": "https://solution.org.in/",
            "source_url": "https://solution.org.in/",
            "application_url": "https://solution.org.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite / Field",
            "fee": "Not specified",
            "category": "Social Development",
            "provider_type": "Non-Profit Organisation",
            "contact_phone": "0657-2346076",
            "contact_email": "solutionngo@gmail.com",
            "map_link": "https://www.google.com/maps/search/?api=1&query=180+Bhuiyadih+Jamshedpur"
        },

        # ==================================================
        # RANCHI - ANUGAT AI
        # ==================================================

        {
            "title": "Founder's Office Intern",
            "company": "Anugat AI",
            "field": "Operations / Research / Sales / Content",
            "location": "Ranchi",
            "duration": "Programme dependent",
            "stipend": "Up to ₹10,000/month including stipend, travel and food allowance",
            "eligibility": "Currently based in Ranchi; no minimum experience required",
            "skills": "Content Creation, Research, Documentation, Sales Support, Google Workspace, Notion, Excel",
            "description": "Current hybrid internship at Anugat AI working across content, operations, coordination, sales support and market research.",
            "apply_link": "https://www.anugatai.com/careers",
            "last_date": "Open - Rolling Basis",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Ranchi, Jharkhand",
            "area": None,
            "city": "Ranchi",
            "official_website": "https://www.anugatai.com/",
            "source_url": "https://www.anugatai.com/careers",
            "application_url": "https://www.anugatai.com/careers",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Hybrid - Ranchi",
            "fee": "No fee mentioned",
            "category": "Technology / Operations",
            "provider_type": "AI Startup",
            "contact_phone": None,
            "contact_email": None,
            "map_link": None
        },

        # ==================================================
        # DHANBAD - CIL INNOVATION & INCUBATION CENTRE
        # ==================================================

        {
            "title": "Internship Scheme 2026",
            "company": "CIL Innovation & Incubation Centre - IIT (ISM) Dhanbad",
            "field": "Innovation / Technology / Industrial Research",
            "location": "Dhanbad",
            "duration": "Programme dependent",
            "stipend": "Programme dependent",
            "eligibility": "Applicants selected under the 2026 Internship Scheme",
            "skills": "Innovation, Industrial Technology, Research, Project Development",
            "description": "Internship Scheme 2026 conducted through the CIL Innovation & Incubation Centre at IIT (ISM) Dhanbad.",
            "apply_link": "https://ciicentre.iitism.ac.in/",
            "last_date": "2026 scheme activity recorded; check official centre for next cycle",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "IIT (ISM) Dhanbad, Dhanbad - 826004, Jharkhand",
            "area": None,
            "city": "Dhanbad",
            "official_website": "https://ciicentre.iitism.ac.in/",
            "source_url": "https://ciicentre.iitism.ac.in/events.php",
            "application_url": "https://ciicentre.iitism.ac.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite / Programme dependent",
            "fee": "Programme dependent",
            "category": "Innovation / Research",
            "provider_type": "Incubation Centre",
            "contact_phone": None,
            "contact_email": None,
            "map_link": "https://www.google.com/maps/search/?api=1&query=CIL+Innovation+Incubation+Centre+IIT+ISM+Dhanbad"
        },

        # ==================================================
        # BOKARO - SAIL BOKARO STEEL PLANT
        # ==================================================

        {
            "title": "PM Internship Scheme - Phase III",
            "company": "SAIL - Bokaro Steel Plant",
            "field": "Industrial / Technical / Management",
            "location": "Bokaro",
            "duration": "9 Months",
            "stipend": "Approx. ₹9,000/month",
            "eligibility": "ITI, Diploma, Graduate and eligible 12th-pass candidates as per PMIS criteria",
            "skills": "Electrical, Mechanical, Fitter, Welder, Turner, Machinist, Civil, Instrumentation, Metallurgy, Logistics, HR, Computer Operations, Programming",
            "description": "PM Internship Scheme Phase III at Bokaro Steel Plant with industrial exposure across technical and non-technical departments.",
            "apply_link": "https://pminternship.mca.gov.in/",
            "last_date": "15 November 2026",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Bokaro Steel Plant, Bokaro Steel City, Jharkhand",
            "area": None,
            "city": "Bokaro",
            "official_website": "https://www.sail.co.in/",
            "source_url": "https://www.jagran.com/jharkhand/bokaro-bokaro-steel-plant-invites-applications-for-pm-internship-40354280.html",
            "application_url": "https://pminternship.mca.gov.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "No application fee mentioned in the cited notice",
            "category": "Industrial Internship",
            "provider_type": "PSU / Steel Plant",
            "contact_phone": None,
            "contact_email": None,
            "map_link": "https://www.google.com/maps/search/?api=1&query=Bokaro+Steel+Plant+Bokaro"
        },

        # ==================================================
        # HAZARIBAGH - APNA
        # ==================================================

        {
            "title": "Internship / Volunteer Programme",
            "company": "APNA - Association for Parivartan of Nation",
            "field": "Social Development / Training / Community Work",
            "location": "Hazaribagh",
            "duration": "Programme dependent",
            "stipend": "Not specified",
            "eligibility": "Students and applicants interested in internship, volunteering and training activities",
            "skills": "Community Development, Training, Research, Field Work",
            "description": "APNA provides opportunities to intern, volunteer and train with its organisation. Hazaribagh office is located near Model Anganwadi on Bania Road.",
            "apply_link": "https://www.parivartan.org/get-involved",
            "last_date": "Check official website",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Bania Rd, Near Model Anganwadi, Hazaribagh, Nawada, Jharkhand - 825302",
            "area": "Bania Road",
            "city": "Hazaribagh",
            "official_website": "https://www.parivartan.org/",
            "source_url": "https://www.parivartan.org/get-involved",
            "application_url": "https://www.parivartan.org/get-involved",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite / Field",
            "fee": "Not specified",
            "category": "Social Development",
            "provider_type": "Non-Profit Organisation",
            "contact_phone": None,
            "contact_email": "contact@parivartan.org",
            "map_link": "https://www.google.com/maps/search/?api=1&query=Bania+Road+Hazaribagh+Jharkhand"
        },

        # ==================================================
        # DEOGHAR - BIT MESRA DEOGHAR
        # ==================================================

        {
            "title": "Project / Industry Internship - CSE",
            "company": "Birla Institute of Technology, Deoghar Campus",
            "field": "Computer Science & Engineering",
            "location": "Deoghar",
            "duration": "Programme dependent",
            "stipend": "Programme dependent",
            "eligibility": "Eligible students of the programme as per institute requirements",
            "skills": "Computer Science, Industry Projects, Software / Technical Skills",
            "description": "The CSE department at BIT Deoghar lists Project / Industry Internship among its departmental activities, with an assigned internship coordinator.",
            "apply_link": "https://bitmesra.ac.in/",
            "last_date": "Check official campus / department notice",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "BIT Off Campus Deoghar, Deoghar, Jharkhand - 814142",
            "area": None,
            "city": "Deoghar",
            "official_website": "https://bitmesra.ac.in/",
            "source_url": "https://bitmesra.ac.in/edudepartment/content/4/107/200",
            "application_url": "https://bitmesra.ac.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Campus / Programme dependent",
            "fee": "Programme dependent",
            "category": "Computer Science & IT",
            "provider_type": "Technical Institute",
            "contact_phone": None,
            "contact_email": None,
            "map_link": "https://www.google.com/maps/search/?api=1&query=BIT+Deoghar+Jharkhand"
        }
    ]

    added = 0

    for item in opportunities:

        existing = conn.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            continue

        columns = ", ".join(item.keys())

        placeholders = ", ".join(
            ["?"] * len(item)
        )

        conn.execute(
            f"""
            INSERT INTO internships (
                {columns}
            )
            VALUES (
                {placeholders}
            )
            """,
            tuple(item.values())
        )

        added += 1

    conn.commit()
    conn.close()

    print()
    print(
        f"{added} unique verified centres/programmes "
        f"from batch 3 added successfully."
    )

    # ==================================================
# UNIQUE VERIFIED CENTRES - BATCH 4
# ==================================================

def add_unique_centres_batch_4():

    conn = get_db_connection()

    today = datetime.now().strftime("%Y-%m-%d")

    opportunities = [

        # ==================================================
        # JAMSHEDPUR - CSIR NML
        # ==================================================

        {
            "title": "Summer Internship Programme 2026",
            "company": "CSIR - National Metallurgical Laboratory",
            "field": "Metallurgy / Materials / Mechanical / Chemical / Mineral Engineering",
            "location": "Jamshedpur",
            "duration": "Minimum 45 Days",
            "stipend": "Not specified",
            "eligibility": "Third-year undergraduate engineering students as per CSIR-NML 2026 internship guidelines",
            "skills": "Metallurgical Engineering, Materials Science, Mechanical Engineering, Chemical Engineering, Mineral Engineering, Waste Management",
            "description": "CSIR-NML Jamshedpur conducted its 2026 Summer Internship programme for eligible undergraduate engineering students with training in specified engineering and materials-related subject areas.",
            "apply_link": "https://nml.res.in/",
            "last_date": "2026 cycle completed - check CSIR-NML for next cycle",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "CSIR-National Metallurgical Laboratory, Jamshedpur, Jharkhand - 831007",
            "area": None,
            "city": "Jamshedpur",
            "official_website": "https://nml.res.in/",
            "source_url": "https://nml.res.in/archived-notification?page=2",
            "application_url": "https://nml.res.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check official notification",
            "category": "Engineering / Research",
            "provider_type": "CSIR Government Laboratory",
            "contact_phone": None,
            "contact_email": "aksahu.nml@csir.res.in",
            "map_link": "https://www.google.com/maps/search/?api=1&query=CSIR+National+Metallurgical+Laboratory+Jamshedpur"
        },

        # ==================================================
        # JAMSHEDPUR - NSTI
        # ==================================================

        {
            "title": "Industrial Skill Training Programme",
            "company": "National Skill Training Institute - Jamshedpur",
            "field": "Industrial / Vocational Training",
            "location": "Jamshedpur",
            "duration": "Programme dependent",
            "stipend": "Not specified",
            "eligibility": "Applicants eligible for the respective NSTI training programme",
            "skills": "Fitter, Turner, Machinist, Electrician, COPA, Automobile, Solar Technician, IoT",
            "description": "Government of India skill-training institute conducting vocational, advanced and instructor training programmes for industrial skill development.",
            "apply_link": "https://nstijamshedpur.dgt.gov.in/",
            "last_date": "Check current admission / training notice",
            "created_at": today,
            "opportunity_type": "Training",
            "address": "National Skill Training Institute, Govt. Polytechnic Campus, Adityapur, Jamshedpur, Jharkhand - 832109",
            "area": "Adityapur",
            "city": "Jamshedpur",
            "official_website": "https://nstijamshedpur.dgt.gov.in/",
            "source_url": "https://nstijamshedpur.dgt.gov.in/",
            "application_url": "https://nstijamshedpur.dgt.gov.in/",
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Offline",
            "fee": "Programme dependent",
            "category": "Industrial Training",
            "provider_type": "Government Training Institute",
            "contact_phone": "0657-2383470",
            "contact_email": "nsti-jamshedpur@dgt.gov.in",
            "map_link": "https://www.google.com/maps/search/?api=1&query=National+Skill+Training+Institute+Adityapur+Jamshedpur"
        },

        # ==================================================
        # HAZARIBAGH - UNMASKED CYBER SECURITY
        # ==================================================

        {
            "title": "Cyber Security Summer Internship & Bootcamp 2026",
            "company": "Unmasked Cyber Security Private Limited",
            "field": "Cyber Security / Networking",
            "location": "Hazaribagh",
            "duration": "June - July 2026",
            "stipend": "Not specified",
            "eligibility": "Students interested in technology, cybersecurity, ethical hacking, networking and digital security",
            "skills": "Kali Linux, Wireshark, Burp Suite, Nmap, Metasploit, Networking, Cyber Security",
            "description": "Cyber Security Summer Internship and Bootcamp 2026 in Hazaribagh covering practical networking, cybersecurity concepts, ethical-hacking tools and hands-on training.",
            "apply_link": "https://www.linkedin.com/",
            "last_date": "2026 programme completed - check provider for next batch",
            "created_at": today,
            "opportunity_type": "Internship",
            "address": "Hazaribagh, Jharkhand",
            "area": None,
            "city": "Hazaribagh",
            "official_website": None,
            "source_url": "https://samridhjharkhand.com/state/jharkhand/hazaribagh/hazaribagh-news-first-week-of-cyber-security-summer-internship-completed/article-22881",
            "application_url": None,
            "verification_status": "Verified",
            "verified_at": today,
            "mode": "Onsite",
            "fee": "Check provider",
            "category": "Cyber Security",
            "provider_type": "Cyber Security Company",
            "contact_phone": "+91 9508553365 / +91 7303663034",
            "contact_email": "unmasked006@gmail.com",
            "map_link": "https://www.google.com/maps/search/?api=1&query=Unmasked+Cyber+Security+Hazaribagh+Jharkhand"
        }
    ]

    added = 0

    for item in opportunities:

        existing = conn.execute(
            """
            SELECT id
            FROM internships
            WHERE title = ?
              AND company = ?
              AND city = ?
            """,
            (
                item["title"],
                item["company"],
                item["city"]
            )
        ).fetchone()

        if existing:
            continue

        columns = ", ".join(item.keys())

        placeholders = ", ".join(
            ["?"] * len(item)
        )

        conn.execute(
            f"""
            INSERT INTO internships (
                {columns}
            )
            VALUES (
                {placeholders}
            )
            """,
            tuple(item.values())
        )

        added += 1

    conn.commit()
    conn.close()

    print()
    print(
        f"{added} unique verified centres "
        f"from batch 4 added successfully."
    )
# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print(" CAREER & INTERNSHIP NETWORK")
    print(" REAL DATABASE SETUP")
    print("========================================")

    print()
    print(
        "DATABASE FILE:"
    )

    print(DATABASE)

    print()

    # Step 1
    create_tables()

    # Step 1A
    create_institutes_table()
    add_verified_jharkhand_institutes()

    # Step 2
    remove_old_demo_data()

    # Step 3
    add_real_opportunities()

     # Step 4
    add_new_jharkhand_opportunities()

    # Step 5
    add_more_real_opportunities()

# Step 6
add_more_verified_opportunities_batch_2()


# Step 7
add_unique_centres_batch_3()

# Step 8
add_unique_centres_batch_4()

# Step 5 - Dhanbad Opportunities
add_dhanbad_opportunities()

print()
print("========================================")
print(" DATABASE SETUP COMPLETED")
print("========================================")