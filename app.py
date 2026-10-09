from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database_pg import (get_db_connection, create_tables)

app = Flask(__name__)

# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = "career_internship_network_secret_key"


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

create_tables()

@app.route("/sitemap.xml")
def sitemap():
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://jd-career-tech.vercel.app/home</loc>
    </url>
    <url>
        <loc>https://jd-career-tech.vercel.app/internships</loc>
    </url>
    <url>
        <loc>https://jd-career-tech.vercel.app/institutes</loc>
    </url>
</urlset>"""

    return app.response_class(
        sitemap_xml,
        mimetype="application/xml"
    )
@app.route("/")
def index():
    return redirect(url_for("home"))


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/home")
def home():
    conn = get_db_connection()

    total_opportunities = conn.execute(
        "SELECT COUNT(*) AS total FROM internships"
    ).fetchone()["total"]

    total_fields = conn.execute(
        "SELECT COUNT(DISTINCT field) AS total FROM internships"
    ).fetchone()["total"]

    total_cities = conn.execute(
        "SELECT COUNT(DISTINCT city) AS total FROM internships"
    ).fetchone()["total"]

    total_organizations = conn.execute(
        "SELECT COUNT(DISTINCT company) AS total FROM internships"
    ).fetchone()["total"]

    opportunity_types = conn.execute(
        "SELECT COUNT(DISTINCT opportunity_type) AS total FROM internships"
    ).fetchone()["total"]

    career_progress = 0

    if "student_id" in session:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (session["student_id"],)
        ).fetchone()

        if student:
            fields = [
                student["name"],
                student["email"],
                student["education"],
                student["branch"],
                student["year"],
                student["city"]
            ]

            completed = sum(1 for field in fields if field)
            career_progress = int((completed / len(fields)) * 100)

    conn.close()

    return render_template(
        "home.html",
        total_opportunities=total_opportunities,
        total_fields=total_fields,
        total_cities=total_cities,
        total_organizations=total_organizations,
        opportunity_types=opportunity_types,
        career_progress=career_progress
    )

# =========================================================
# INTERNSHIPS / TRAINING PAGE
# =========================================================

@app.route("/internships")
def internships():

    search = request.args.get(
        "search",
        ""
    ).strip()

    field = request.args.get(
        "field",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    opportunity_type = request.args.get(
        "opportunity_type",
        ""
    ).strip()

    area = request.args.get(
        "area",
        ""
    ).strip()

    connection = get_db_connection()

    # =====================================================
    # MAIN QUERY
    # =====================================================

    query = """
        SELECT *
        FROM internships
        WHERE 1 = 1
    """

    parameters = []

    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                LOWER(title) LIKE ?
                OR LOWER(company) LIKE ?
                OR LOWER(field) LIKE ?
                OR LOWER(skills) LIKE ?
                OR LOWER(description) LIKE ?
                OR LOWER(city) LIKE ?
                OR LOWER(area) LIKE ?
                OR LOWER(address) LIKE ?
                OR LOWER(category) LIKE ?
                OR LOWER(provider_type) LIKE ?
                OR LOWER(opportunity_type) LIKE ?
            )
        """

        search_value = f"%{search.lower()}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # =====================================================
    # FIELD FILTER
    # =====================================================

    if field:

        query += """
            AND LOWER(field) LIKE ?
        """

        parameters.append(
            f"%{field.lower()}%"
        )

    # =====================================================
    # CITY / LOCATION FILTER
    # =====================================================

    if location:

        if location.lower() == "remote":

            query += """
                AND (
                    LOWER(location) = 'remote'
                    OR LOWER(mode) LIKE '%online%'
                    OR LOWER(mode) LIKE '%remote%'
                    OR LOWER(mode) LIKE '%work from home%'
                )
            """

        else:

            query += """
                AND (
                    LOWER(city) LIKE ?
                    OR LOWER(location) LIKE ?
                    OR LOWER(address) LIKE ?
                )
            """

            location_value = (
                f"%{location.lower()}%"
            )

            parameters.extend([
                location_value,
                location_value,
                location_value
            ])

    # =====================================================
    # OPPORTUNITY TYPE FILTER
    # =====================================================

    if opportunity_type:

        query += """
            AND LOWER(opportunity_type) = ?
        """

        parameters.append(
            opportunity_type.lower()
        )

    # =====================================================
    # AREA FILTER
    # =====================================================

    if area:

        query += """
            AND LOWER(area) LIKE ?
        """

        parameters.append(
            f"%{area.lower()}%"
        )

    # =====================================================
    # ORDER
    # =====================================================

    query += """
        ORDER BY
            CASE
                WHEN LOWER(verification_status) = 'verified'
                THEN 0
                ELSE 1
            END,
            id DESC
    """

    internship_rows = connection.execute(
        query,
        parameters
    ).fetchall()

    # =====================================================
    # SMART FILTER OPTIONS
    #
    # If city is selected:
    # Area + Field + Type will be city specific.
    #
    # =====================================================

    if location and location.lower() != "remote":

        filter_rows = connection.execute(
            """
            SELECT DISTINCT
                area,
                field,
                opportunity_type
            FROM internships
            WHERE LOWER(city) = LOWER(?)
            """,
            (location,)
        ).fetchall()

    else:

        filter_rows = connection.execute(
            """
            SELECT DISTINCT
                area,
                field,
                opportunity_type
            FROM internships
            """
        ).fetchall()

    # =====================================================
    # CITY LIST
    # =====================================================

    locations = connection.execute(
        """
        SELECT DISTINCT city
        FROM internships
        WHERE city IS NOT NULL
        AND TRIM(city) != ''
        ORDER BY city
        """
    ).fetchall()

    # =====================================================
    # AREAS
    # =====================================================

    areas = sorted({
        row["area"]
        for row in filter_rows
        if row["area"]
        and str(row["area"]).strip()
    })

    # =====================================================
    # FIELDS
    # =====================================================

    fields = sorted({
        row["field"]
        for row in filter_rows
        if row["field"]
        and str(row["field"]).strip()
    })

    # =====================================================
    # OPPORTUNITY TYPES
    # =====================================================

    opportunity_types = sorted({
        row["opportunity_type"]
        for row in filter_rows
        if row["opportunity_type"]
        and str(row["opportunity_type"]).strip()
    })

    # =====================================================
    # SAVED INTERNSHIPS
    # =====================================================

    saved_ids = set()

    if session.get("student_id"):

        saved_rows = connection.execute(
            """
            SELECT internship_id
            FROM saved_internships
            WHERE student_id = ?
            """,
            (session["student_id"],)
        ).fetchall()

        saved_ids = {
            row["internship_id"]
            for row in saved_rows
        }

    connection.close()

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "internships.html",

        internships=internship_rows,

        fields=fields,

        locations=locations,

        areas=areas,

        opportunity_types=opportunity_types,

        search=search,

        selected_field=field,

        selected_location=location,

        selected_area=area,

        selected_opportunity_type=opportunity_type,

        saved_ids=saved_ids,

        near_me=False,

        student_city=""
    )


# =========================================================
# SMART FILTER OPTIONS
# =========================================================
#
# Used by internships.html JavaScript.
#
# City select karne par:
#
# City
#   ↓
# Area
#   ↓
# Field
#   ↓
# Opportunity Type
#
# sab database ke according dynamically update honge.
# =========================================================
@app.route("/filter-options")
def filter_options():

    connection = get_db_connection()

    city = request.args.get("city", "").strip()

    # ---------------------------------
    # CITY SELECTED
    # ---------------------------------
    if city:

        # Areas only for selected city
        areas = connection.execute("""
            SELECT DISTINCT area
            FROM internships
            WHERE city = ?
              AND area IS NOT NULL
              AND TRIM(area) != ''
            ORDER BY area ASC
        """, (city,)).fetchall()

        # Fields only for selected city
        fields = connection.execute("""
            SELECT DISTINCT field
            FROM internships
            WHERE city = ?
              AND field IS NOT NULL
              AND TRIM(field) != ''
            ORDER BY field ASC
        """, (city,)).fetchall()

        # Opportunity types only for selected city
        opportunity_types = connection.execute("""
            SELECT DISTINCT opportunity_type
            FROM internships
            WHERE city = ?
              AND opportunity_type IS NOT NULL
              AND TRIM(opportunity_type) != ''
            ORDER BY opportunity_type ASC
        """, (city,)).fetchall()

    # ---------------------------------
    # NO CITY SELECTED
    # ---------------------------------
    else:

        areas = connection.execute("""
            SELECT DISTINCT area
            FROM internships
            WHERE area IS NOT NULL
              AND TRIM(area) != ''
            ORDER BY area ASC
        """).fetchall()

        fields = connection.execute("""
            SELECT DISTINCT field
            FROM internships
            WHERE field IS NOT NULL
              AND TRIM(field) != ''
            ORDER BY field ASC
        """).fetchall()

        opportunity_types = connection.execute("""
            SELECT DISTINCT opportunity_type
            FROM internships
            WHERE opportunity_type IS NOT NULL
              AND TRIM(opportunity_type) != ''
            ORDER BY opportunity_type ASC
        """).fetchall()

    connection.close()

    return jsonify({
        "areas": [
            row["area"]
            for row in areas
            if row["area"]
        ],

        "fields": [
            row["field"]
            for row in fields
            if row["field"]
        ],

        "opportunity_types": [
            row["opportunity_type"]
            for row in opportunity_types
            if row["opportunity_type"]
        ]
    })

    
# =========================================================
# DIRECT CITY → AREA API
# =========================================================
#
# Future advanced location system ke liye.
#
# Example:
#
# /api/internship-areas?city=Ranchi
#
# =========================================================

@app.route("/api/internship-areas")
def internship_areas():

    city = request.args.get(
        "city",
        ""
    ).strip()

    connection = get_db_connection()

    if city:

        rows = connection.execute(
            """
            SELECT DISTINCT area
            FROM internships
            WHERE LOWER(city) = LOWER(?)
            AND area IS NOT NULL
            AND TRIM(area) != ''
            ORDER BY area
            """,
            (city,)
        ).fetchall()

    else:

        rows = connection.execute(
            """
            SELECT DISTINCT area
            FROM internships
            WHERE area IS NOT NULL
            AND TRIM(area) != ''
            ORDER BY area
            """
        ).fetchall()

    connection.close()

    return jsonify([
        {
            "area": row["area"]
        }
        for row in rows
    ])


# =========================================================
# INSTITUTES DIRECTORY
# =========================================================

@app.route("/institutes")
def institutes():

    connection = get_db_connection()

    city = request.args.get(
        "city",
        ""
    ).strip()

    institute_type = request.args.get(
        "type",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = """
        SELECT *
        FROM institutes
        WHERE 1 = 1
    """

    params = []

    # =====================================================
    # CITY
    # =====================================================

    if city:

        query += """
            AND LOWER(city) = LOWER(?)
        """

        params.append(city)

    # =====================================================
    # TYPE
    # =====================================================

    if institute_type:

        query += """
            AND LOWER(institute_type) = LOWER(?)
        """

        params.append(
            institute_type
        )

    # =====================================================
    # CATEGORY
    # =====================================================

    if category:

        query += """
            AND LOWER(category) = LOWER(?)
        """

        params.append(
            category
        )

    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                LOWER(name) LIKE LOWER(?)
                OR LOWER(city) LIKE LOWER(?)
                OR LOWER(area) LIKE LOWER(?)
                OR LOWER(institute_type) LIKE LOWER(?)
                OR LOWER(courses) LIKE LOWER(?)
            )
        """

        search_value = (
            f"%{search}%"
        )

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # =====================================================
    # ORDER
    # =====================================================

    query += """
        ORDER BY
            city ASC,
            name ASC
    """

    institutes_list = connection.execute(
        query,
        params
    ).fetchall()

    # =====================================================
    # CITIES
    # =====================================================

    cities = connection.execute(
        """
        SELECT DISTINCT city
        FROM institutes
        WHERE city IS NOT NULL
        AND city != ''
        ORDER BY city
        """
    ).fetchall()

    # =====================================================
    # INSTITUTE TYPES
    # =====================================================

    institute_types = connection.execute(
        """
        SELECT DISTINCT institute_type
        FROM institutes
        WHERE institute_type IS NOT NULL
        AND institute_type != ''
        ORDER BY institute_type
        """
    ).fetchall()

    # =====================================================
    # CATEGORIES
    # =====================================================

    categories = connection.execute(
        """
        SELECT DISTINCT category
        FROM institutes
        WHERE category IS NOT NULL
        AND category != ''
        ORDER BY category
        """
    ).fetchall()

    # =====================================================
    # TOTAL COUNT
    # =====================================================

    total_count = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM institutes
        """
    ).fetchone()["total"]

    # =====================================================
    # FILTERED COUNT
    # =====================================================

    filtered_count = len(
        institutes_list
    )

    connection.close()

    return render_template(
        "institutes.html",

        institutes=institutes_list,

        cities=cities,

        institute_types=institute_types,

        categories=categories,

        total_count=total_count,

        filtered_count=filtered_count,

        selected_city=city,

        selected_type=institute_type,

        selected_category=category,

        search_query=search
    )


# =========================================================
# INTERNSHIPS NEAR ME
# =========================================================

@app.route("/near-me")
def near_me():

    if "student_id" not in session:

        flash(
            "Please login first to find opportunities near you.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    # =====================================================
    # GET STUDENT CITY
    # =====================================================

    student = connection.execute(
        """
        SELECT city
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    if student is None:

        connection.close()

        flash(
            "Student profile not found.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    city = (
        student["city"] or ""
    ).strip()

    if not city:

        connection.close()

        flash(
            "Please add your city in your profile first.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    # =====================================================
    # CITY + AREA + REMOTE
    # =====================================================

    city_value = (
        f"%{city.lower()}%"
    )

    internships_near_me = connection.execute(
        """
        SELECT *
        FROM internships
        WHERE
            LOWER(city) LIKE ?
            OR LOWER(location) LIKE ?
            OR LOWER(area) LIKE ?
            OR LOWER(address) LIKE ?
            OR LOWER(location) = 'remote'
            OR LOWER(mode) LIKE '%online%'
            OR LOWER(mode) LIKE '%remote%'
            OR LOWER(mode) LIKE '%work from home%'

        ORDER BY

            CASE
                WHEN LOWER(city) LIKE ?
                THEN 0

                WHEN LOWER(area) LIKE ?
                THEN 1

                WHEN LOWER(location) LIKE ?
                THEN 2

                ELSE 3
            END,

            CASE
                WHEN LOWER(verification_status) = 'verified'
                THEN 0
                ELSE 1
            END,

            id DESC
        """,
        (
            city_value,
            city_value,
            city_value,
            city_value,

            city_value,
            city_value,
            city_value
        )
    ).fetchall()

    # =====================================================
    # FILTER DATA
    # =====================================================

    fields = connection.execute(
        """
        SELECT DISTINCT field
        FROM internships
        WHERE field IS NOT NULL
        AND field != ''
        ORDER BY field
        """
    ).fetchall()

    locations = connection.execute(
        """
        SELECT DISTINCT city
        FROM internships
        WHERE city IS NOT NULL
        AND city != ''
        ORDER BY city
        """
    ).fetchall()

    areas = connection.execute(
        """
        SELECT DISTINCT area
        FROM internships
        WHERE area IS NOT NULL
        AND area != ''
        ORDER BY area
        """
    ).fetchall()

    opportunity_types = connection.execute(
        """
        SELECT DISTINCT opportunity_type
        FROM internships
        WHERE opportunity_type IS NOT NULL
        AND opportunity_type != ''
        ORDER BY opportunity_type
        """
    ).fetchall()

    # =====================================================
    # SAVED IDS
    # =====================================================

    saved_rows = connection.execute(
        """
        SELECT internship_id
        FROM saved_internships
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchall()

    saved_ids = {
        row["internship_id"]
        for row in saved_rows
    }

    connection.close()

    return render_template(
        "internships.html",

        internships=internships_near_me,

        fields=fields,

        locations=locations,

        areas=areas,

        opportunity_types=opportunity_types,

        search="",

        selected_field="",

        selected_location="",

        selected_area="",

        selected_opportunity_type="",

        saved_ids=saved_ids,

        near_me=True,

        student_city=city
    )


# =========================================================
# INTERNSHIP DETAILS
# =========================================================

@app.route("/internship-details")
def internship_details():

    internship_id = request.args.get(
        "id"
    )

    if not internship_id:

        return redirect(
            url_for("internships")
        )

    connection = get_db_connection()

    internship = connection.execute(
        """
        SELECT *
        FROM internships
        WHERE id = ?
        """,
        (internship_id,)
    ).fetchone()

    is_saved = False

    if session.get("student_id") and internship:

        saved = connection.execute(
            """
            SELECT id
            FROM saved_internships
            WHERE student_id = ?
            AND internship_id = ?
            """,
            (
                session["student_id"],
                internship["id"]
            )
        ).fetchone()

        if saved:

            is_saved = True

    connection.close()

    if not internship:

        return "Opportunity not found", 404

    return render_template(
        "internship_details.html",
        internship=internship,
        is_saved=is_saved
    )


# =========================================================
# CAREER GUIDE
# =========================================================

@app.route("/career")
def career():

    return render_template(
        "career.html"
    )


# =========================================================
# INTERNSHIP DECISION ASSISTANT
# =========================================================

@app.route(
    "/decision-assistant",
    methods=["GET", "POST"]
)
def decision_assistant():

    # =====================================================
    # DEFAULT DATA
    # =====================================================

    assistant_data = {
        "education": "",
        "branch": "",
        "year": "",
        "city": "",
        "interest": "",
        "skills": "",
        "experience": ""
    }

    # =====================================================
    # GET REQUEST
    # =====================================================

    if request.method == "GET":

        if session.get("student_id"):

            connection = get_db_connection()

            student = connection.execute(
                """
                SELECT
                    education,
                    branch,
                    year,
                    city
                FROM students
                WHERE id = ?
                """,
                (session["student_id"],)
            ).fetchone()

            connection.close()

            if student:

                assistant_data["education"] = (
                    student["education"] or ""
                )

                assistant_data["branch"] = (
                    student["branch"] or ""
                )

                assistant_data["year"] = (
                    student["year"] or ""
                )

                assistant_data["city"] = (
                    student["city"] or ""
                )

        return render_template(
            "decision_assistant.html",
            recommendations=None,
            assistant_data=assistant_data
        )

    # =====================================================
    # FORM DATA
    # =====================================================

    education = request.form.get(
        "education",
        ""
    ).strip()

    branch = request.form.get(
        "branch",
        ""
    ).strip()

    year = request.form.get(
        "year",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    interest = request.form.get(
        "interest",
        ""
    ).strip()

    skills = request.form.get(
        "skills",
        ""
    ).strip()

    experience = request.form.get(
        "experience",
        ""
    ).strip()

    # =====================================================
    # LOAD PROFILE DATA
    # =====================================================

    if session.get("student_id"):

        connection = get_db_connection()

        student = connection.execute(
            """
            SELECT
                education,
                branch,
                year,
                city
            FROM students
            WHERE id = ?
            """,
            (session["student_id"],)
        ).fetchone()

        connection.close()

        if student:

            if not education:
                education = student["education"] or ""

            if not branch:
                branch = student["branch"] or ""

            if not year:
                year = student["year"] or ""

            if not city:
                city = student["city"] or ""

    # =====================================================
    # VALIDATION
    # =====================================================

    if (
        not education
        or not branch
        or not year
        or not city
        or not interest
        or not experience
    ):

        flash(
            "Please complete all required fields.",
            "error"
        )

        assistant_data = {
            "education": education,
            "branch": branch,
            "year": year,
            "city": city,
            "interest": interest,
            "skills": skills,
            "experience": experience
        }

        return render_template(
            "decision_assistant.html",
            recommendations=None,
            assistant_data=assistant_data
        )

    # =====================================================
    # DATABASE
    # =====================================================

    connection = get_db_connection()

    opportunities = connection.execute(
        """
        SELECT *
        FROM internships
        ORDER BY
            CASE
                WHEN LOWER(verification_status) = 'verified'
                THEN 0
                ELSE 1
            END,
            id DESC
        """
    ).fetchall()

    connection.close()

    # =====================================================
    # USER VALUES
    # =====================================================

    user_city = city.lower().strip()

    user_interest = interest.lower().strip()

    user_branch = branch.lower().strip()

    user_education = education.lower().strip()

    user_experience = experience.lower().strip()

    # =====================================================
    # USER SKILLS
    # =====================================================

    user_skills = [
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ]

    # =====================================================
    # HELPER
    # =====================================================

    def contains_any(text, keywords):

        text = text.lower()

        for keyword in keywords:

            if keyword and keyword in text:

                return True

        return False

    # =====================================================
    # INTEREST GROUPS
    # =====================================================

    interest_groups = {

        "web": [
            "web",
            "web development",
            "website",
            "frontend",
            "backend",
            "full stack",
            "fullstack"
        ],

        "software": [
            "software",
            "software development",
            "programming",
            "application development",
            "app development"
        ],

        "data": [
            "data",
            "data analytics",
            "data analysis",
            "analytics",
            "database",
            "sql"
        ],

        "ai": [
            "ai",
            "artificial intelligence",
            "machine learning",
            "ml"
        ],

        "cloud": [
            "cloud",
            "aws",
            "azure",
            "devops"
        ],

        "networking": [
            "network",
            "networking",
            "computer network",
            "ccna"
        ],

        "cybersecurity": [
            "cyber",
            "cybersecurity",
            "security",
            "ethical hacking"
        ],

        "design": [
            "design",
            "graphic design",
            "ui",
            "ux",
            "ui/ux"
        ],

        "marketing": [
            "marketing",
            "digital marketing",
            "social media",
            "content"
        ],

        "hr": [
            "hr",
            "human resource",
            "human resources"
        ],

        "finance": [
            "finance",
            "accounting",
            "accounts",
            "tally"
        ]
    }

    # =====================================================
    # FIND INTEREST CATEGORY
    # =====================================================

    selected_interest_keywords = []

    for group_keywords in interest_groups.values():

        if contains_any(
            user_interest,
            group_keywords
        ):

            selected_interest_keywords.extend(
                group_keywords
            )

    if not selected_interest_keywords:

        selected_interest_keywords = [
            user_interest
        ]

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    recommendations = []

    # =====================================================
    # MATCH OPPORTUNITIES
    # =====================================================

    for opportunity in opportunities:

        score = 0

        reasons = []

        # -------------------------------------------------
        # DATABASE VALUES
        # -------------------------------------------------

        title = (
            opportunity["title"] or ""
        ).lower()

        field = (
            opportunity["field"] or ""
        ).lower()

        location = (
            opportunity["location"] or ""
        ).lower()

        opportunity_city = (
            opportunity["city"] or ""
        ).lower()

        area = (
            opportunity["area"] or ""
        ).lower()

        eligibility = (
            opportunity["eligibility"] or ""
        ).lower()

        opportunity_skills = (
            opportunity["skills"] or ""
        ).lower()

        description = (
            opportunity["description"] or ""
        ).lower()

        category = (
            opportunity["category"] or ""
        ).lower()

        opportunity_type = (
            opportunity["opportunity_type"]
            or "Internship"
        )

        mode = (
            opportunity["mode"] or ""
        ).lower()

        verification_status = (
            opportunity["verification_status"]
            or ""
        )

        # =================================================
        # SEARCHABLE TEXT
        # =================================================

        searchable_text = " ".join([
            title,
            field,
            eligibility,
            opportunity_skills,
            description,
            category,
            opportunity_city,
            location,
            area
        ])

        # =================================================
        # 1. INTEREST
        # =================================================

        interest_matched = False

        for keyword in selected_interest_keywords:

            if (
                keyword
                and keyword in searchable_text
            ):

                interest_matched = True
                break

        if interest_matched:

            score += 30

            reasons.append(
                "Matches your selected career interest."
            )

        # =================================================
        # 2. CITY
        # =================================================

        if user_city:

            if user_city in opportunity_city:

                score += 30

                reasons.append(
                    "Available in your selected city."
                )

            elif user_city in location:

                score += 25

                reasons.append(
                    "Location matches your preferred city."
                )

            elif user_city in area:

                score += 20

                reasons.append(
                    "Available around your preferred area."
                )

        # =================================================
        # 3. REMOTE / ONLINE
        # =================================================

        if (
            "remote" in location
            or "online" in location
            or "remote" in mode
            or "online" in mode
            or "work from home" in mode
        ):

            score += 10

            reasons.append(
                "Online/remote option is available."
            )

        # =================================================
        # 4. EDUCATION
        # =================================================

        education_keywords = [
            word
            for word in user_education.split()
            if len(word) > 2
        ]

        education_match = False

        for word in education_keywords:

            if word in eligibility:

                education_match = True
                break

        if education_match:

            score += 20

            reasons.append(
                "Your education appears in the eligibility information."
            )

        # =================================================
        # 5. BRANCH
        # =================================================

        branch_keywords = [
            word
            for word in user_branch
            .replace("/", " ")
            .replace("-", " ")
            .split()
            if len(word) > 2
        ]

        branch_match = False

        for word in branch_keywords:

            if (
                word in field
                or word in category
                or word in opportunity_skills
                or word in title
                or word in description
            ):

                branch_match = True
                break

        if branch_match:

            score += 15

            reasons.append(
                "Related to your academic branch."
            )

        # =================================================
        # 6. SKILLS
        # =================================================

        matched_skills = []

        for skill in user_skills:

            if skill in opportunity_skills:

                matched_skills.append(
                    skill
                )

        if matched_skills:

            skill_score = min(
                len(matched_skills) * 5,
                15
            )

            score += skill_score

            reasons.append(
                "Matches your existing skills."
            )

        # =================================================
        # 7. EXPERIENCE
        # =================================================

        if user_experience:

            experience_text = (
                user_experience.lower()
            )

            if (
                "beginner" in experience_text
                or "fresher" in experience_text
                or "no experience" in experience_text
                or "none" in experience_text
                or "student" in experience_text
            ):

                if (
                    "beginner" in eligibility
                    or "fresher" in eligibility
                    or "student" in eligibility
                    or "no experience" in eligibility
                    or "0 experience" in eligibility
                ):

                    score += 10

                    reasons.append(
                        "Suitable for a beginner/fresher profile."
                    )

            elif (
                "beginner" not in experience_text
                and "fresher" not in experience_text
                and "none" not in experience_text
            ):

                if (
                    "experience" in description
                    or "experience" in eligibility
                    or "project" in description
                ):

                    score += 5

                    reasons.append(
                        "Your experience can be relevant to this opportunity."
                    )

        # =================================================
        # 8. VERIFIED
        # =================================================

        if (
            verification_status.lower()
            == "verified"
        ):

            score += 5

            reasons.append(
                "Opportunity information is marked as verified."
            )

        # =================================================
        # 9. OPPORTUNITY TYPE
        # =================================================

        if opportunity_type:

            if (
                "internship"
                in opportunity_type.lower()
            ):

                if (
                    "student" in user_education
                    or "diploma" in user_education
                    or "b.tech" in user_education
                    or "bca" in user_education
                    or "bsc" in user_education
                ):

                    score += 5

                    reasons.append(
                        "Internship format matches a student profile."
                    )

        # =================================================
        # REMOVE DUPLICATE REASONS
        # =================================================

        reasons = list(
            dict.fromkeys(reasons)
        )

        # =================================================
        # KEEP RELEVANT RESULTS
        # =================================================

        if score >= 20:

            match_percentage = min(
                score,
                100
            )

            internship_data = dict(
                opportunity
            )

            internship_data["apply_link"] = (
                internship_data.get(
                    "application_url"
                )
                or internship_data.get(
                    "apply_link"
                )
                or ""
            )

            if not internship_data.get(
                "location"
            ):

                internship_data["location"] = (
                    internship_data.get("city")
                    or internship_data.get("area")
                    or ""
                )

            recommendations.append({
                "internship": internship_data,
                "score": match_percentage,
                "reasons": reasons
            })

    # =====================================================
    # SORT
    # =====================================================

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # =====================================================
    # LIMIT
    # =====================================================

    recommendations = recommendations[:12]

    # =====================================================
    # ASSISTANT DATA
    # =====================================================

    assistant_data = {
        "education": education,
        "branch": branch,
        "year": year,
        "city": city,
        "interest": interest,
        "skills": skills,
        "experience": experience
    }

    # =====================================================
    # NO RESULTS
    # =====================================================

    if not recommendations:

        flash(
            "No strong matches found. Try another interest, skill, or city.",
            "info"
        )

    # =====================================================
    # SHOW RESULTS
    # =====================================================

    return render_template(
        "decision_assistant.html",
        recommendations=recommendations,
        assistant_data=assistant_data
    )


# =========================================================
# SIGNUP
# =========================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        education = request.form.get(
            "education",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

        connection = get_db_connection()

        existing = connection.execute(
            """
            SELECT id
            FROM students
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing:

            connection.close()

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

        hashed_password = (
            generate_password_hash(password)
        )

        connection.execute(
            """
            INSERT INTO students
            (
                name,
                email,
                password,
                education,
                branch
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password,
                education,
                branch
            )
        )

        connection.commit()

        connection.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "signup.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        student = connection.execute(
            """
            SELECT *
            FROM students
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if (
            student
            and check_password_hash(
                student["password"],
                password
            )
        ):

            session["student_id"] = (
                student["id"]
            )

            session["student_name"] = (
                student["name"]
            )

            session["student_email"] = (
                student["email"]
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    if not student:

        connection.close()

        session.clear()

        flash(
            "Student account not found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    application_count = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM applications
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()["total"]

    saved_count = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM saved_internships
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()["total"]

    profile_fields = [
        student["name"],
        student["email"],
        student["education"],
        student["branch"],
        student["year"],
        student["city"]
    ]

    completed_fields = sum(
        1
        for field in profile_fields
        if field
        and str(field).strip()
    )

    profile_completion = int(
        (
            completed_fields
            / len(profile_fields)
        ) * 100
    )

    connection.close()

    return render_template(
        "dashboard.html",
        student=student,
        application_count=application_count,
        saved_count=saved_count,
        profile_completion=profile_completion
    )


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "student_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        education = request.form.get(
            "education",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        if not name or not education:

            connection.close()

            flash(
                "Name and education are required.",
                "error"
            )

            return redirect(
                url_for("profile")
            )

        connection.execute(
            """
            UPDATE students
            SET
                name = ?,
                education = ?,
                branch = ?,
                year = ?,
                city = ?
            WHERE id = ?
            """,
            (
                name,
                education,
                branch,
                year,
                city,
                student_id
            )
        )

        connection.commit()

        session["student_name"] = name

        connection.close()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    connection.close()

    if not student:

        session.clear()

        flash(
            "Student account not found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        student=student
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# APPLY
# =========================================================

@app.route(
    "/apply/<int:internship_id>",
    methods=["POST"]
)
def apply_internship(
    internship_id
):

    if "student_id" not in session:

        flash(
            "Please login to apply.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    opportunity = connection.execute(
        """
        SELECT id
        FROM internships
        WHERE id = ?
        """,
        (internship_id,)
    ).fetchone()

    if not opportunity:

        connection.close()

        flash(
            "Opportunity not found.",
            "error"
        )

        return redirect(
            url_for("internships")
        )

    existing = connection.execute(
        """
        SELECT id
        FROM applications
        WHERE student_id = ?
        AND internship_id = ?
        """,
        (
            student_id,
            internship_id
        )
    ).fetchone()

    if existing:

        connection.close()

        flash(
            "You have already applied for this opportunity.",
            "info"
        )

        return redirect(
            url_for(
                "internship_details",
                id=internship_id
            )
        )

    connection.execute(
        """
        INSERT INTO applications
        (
            student_id,
            internship_id
        )
        VALUES (?, ?)
        """,
        (
            student_id,
            internship_id
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Application submitted successfully!",
        "success"
    )

    return redirect(
        url_for(
            "internship_details",
            id=internship_id
        )
    )


# =========================================================
# SAVE INTERNSHIP
# =========================================================

@app.route(
    "/save-internship/<int:internship_id>",
    methods=["POST"]
)
def save_internship(
    internship_id
):

    if "student_id" not in session:

        flash(
            "Please login to save internships.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    internship = connection.execute(
        """
        SELECT id
        FROM internships
        WHERE id = ?
        """,
        (internship_id,)
    ).fetchone()

    if not internship:

        connection.close()

        flash(
            "Opportunity not found.",
            "error"
        )

        return redirect(
            url_for("internships")
        )

    existing = connection.execute(
        """
        SELECT id
        FROM saved_internships
        WHERE student_id = ?
        AND internship_id = ?
        """,
        (
            student_id,
            internship_id
        )
    ).fetchone()

    if existing:

        connection.close()

        flash(
            "This opportunity is already saved.",
            "info"
        )

        return redirect(
            url_for(
                "internship_details",
                id=internship_id
            )
        )

    connection.execute(
        """
        INSERT INTO saved_internships
        (
            student_id,
            internship_id
        )
        VALUES (?, ?)
        """,
        (
            student_id,
            internship_id
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Opportunity saved successfully!",
        "success"
    )

    return redirect(
        url_for(
            "internship_details",
            id=internship_id
        )
    )


# =========================================================
# UNSAVE
# =========================================================

@app.route(
    "/unsave-internship/<int:internship_id>",
    methods=["POST"]
)
def unsave_internship(
    internship_id
):

    if "student_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM saved_internships
        WHERE student_id = ?
        AND internship_id = ?
        """,
        (
            student_id,
            internship_id
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Opportunity removed from saved list.",
        "info"
    )

    return redirect(
        url_for(
            "internship_details",
            id=internship_id
        )
    )


# =========================================================
# SAVED INTERNSHIPS
# =========================================================

@app.route("/saved-internships")
def saved_internships():

    if "student_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    student_id = session["student_id"]

    connection = get_db_connection()

    saved_internships = connection.execute(
        """
        SELECT
            internships.*,
            saved_internships.saved_at

        FROM saved_internships

        INNER JOIN internships
        ON saved_internships.internship_id = internships.id

        WHERE saved_internships.student_id = ?

        ORDER BY saved_internships.saved_at DESC
        """,
        (student_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "saved_internships.html",
        saved_internships=saved_internships
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )