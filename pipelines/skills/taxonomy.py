from typing import List, Dict

TAXONOMY: List[Dict[str, any]] = [
    # --- Programming ---
    {"skill_id": "prog_python", "canonical_name": "Python", "category": "Programming", "aliases": ["python3", "python 3"]},
    {"skill_id": "prog_java", "canonical_name": "Java", "category": "Programming", "aliases": ["java 8", "java 11", "java 17", "core java", "j2ee"]},
    {"skill_id": "prog_csharp", "canonical_name": "C#", "category": "Programming", "aliases": ["c sharp", "c-sharp"]},
    {"skill_id": "prog_cpp", "canonical_name": "C++", "category": "Programming", "aliases": ["cpp", "c plus plus"]},
    {"skill_id": "prog_js", "canonical_name": "JavaScript", "category": "Programming", "aliases": ["js", "es6", "vanilla js", "javascript"]},
    {"skill_id": "prog_ts", "canonical_name": "TypeScript", "category": "Programming", "aliases": ["ts", "type script"]},
    {"skill_id": "prog_go", "canonical_name": "Go", "category": "Programming", "aliases": ["golang", "go lang"]},
    {"skill_id": "prog_rust", "canonical_name": "Rust", "category": "Programming", "aliases": ["rustlang"]},
    {"skill_id": "prog_php", "canonical_name": "PHP", "category": "Programming", "aliases": ["php7", "php8"]},
    {"skill_id": "prog_kotlin", "canonical_name": "Kotlin", "category": "Programming", "aliases": []},
    {"skill_id": "prog_swift", "canonical_name": "Swift", "category": "Programming", "aliases": ["swiftui", "swift ui"]},

    # --- Frontend ---
    {"skill_id": "fe_react", "canonical_name": "React", "category": "Frontend", "aliases": ["reactjs", "react.js", "react js"]},
    {"skill_id": "fe_nextjs", "canonical_name": "Next.js", "category": "Frontend", "aliases": ["nextjs", "next js", "next.js"]},
    {"skill_id": "fe_angular", "canonical_name": "Angular", "category": "Frontend", "aliases": ["angularjs", "angular.js", "angular 2+"]},
    {"skill_id": "fe_vue", "canonical_name": "Vue", "category": "Frontend", "aliases": ["vuejs", "vue.js", "vue js", "vue3", "vue 3"]},
    {"skill_id": "fe_html", "canonical_name": "HTML", "category": "Frontend", "aliases": ["html5", "html 5"]},
    {"skill_id": "fe_css", "canonical_name": "CSS", "category": "Frontend", "aliases": ["css3", "css 3", "sass", "scss"]},
    {"skill_id": "fe_tailwind", "canonical_name": "Tailwind CSS", "category": "Frontend", "aliases": ["tailwind", "tailwindcss"]},

    # --- Backend ---
    {"skill_id": "be_nodejs", "canonical_name": "Node.js", "category": "Backend", "aliases": ["node", "nodejs", "node js", "express", "expressjs", "express.js"]},
    {"skill_id": "be_dotnet", "canonical_name": ".NET", "category": "Backend", "aliases": ["dot net", ".net core", "dotnet", "asp.net"]},
    {"skill_id": "be_springboot", "canonical_name": "Spring Boot", "category": "Backend", "aliases": ["springboot", "spring-boot", "spring framework"]},
    {"skill_id": "be_django", "canonical_name": "Django", "category": "Backend", "aliases": ["django framework"]},
    {"skill_id": "be_fastapi", "canonical_name": "FastAPI", "category": "Backend", "aliases": ["fast api"]},
    {"skill_id": "be_laravel", "canonical_name": "Laravel", "category": "Backend", "aliases": []},

    # --- Data ---
    {"skill_id": "data_sql", "canonical_name": "SQL", "category": "Data", "aliases": ["t-sql", "pl/sql", "tsql"]},
    {"skill_id": "data_postgres", "canonical_name": "PostgreSQL", "category": "Data", "aliases": ["postgres", "postgre sql", "postgresql"]},
    {"skill_id": "data_mysql", "canonical_name": "MySQL", "category": "Data", "aliases": ["my sql"]},
    {"skill_id": "data_mongo", "canonical_name": "MongoDB", "category": "Data", "aliases": ["mongo", "mongo db"]},
    {"skill_id": "data_redis", "canonical_name": "Redis", "category": "Data", "aliases": []},
    {"skill_id": "data_elastic", "canonical_name": "Elasticsearch", "category": "Data", "aliases": ["elastic search", "elk"]},
    {"skill_id": "data_spark", "canonical_name": "Apache Spark", "category": "Data", "aliases": ["spark", "pyspark"]},
    {"skill_id": "data_kafka", "canonical_name": "Apache Kafka", "category": "Data", "aliases": ["kafka"]},

    # --- Cloud ---
    {"skill_id": "cloud_aws", "canonical_name": "AWS", "category": "Cloud", "aliases": ["amazon web services", "aws cloud"]},
    {"skill_id": "cloud_azure", "canonical_name": "Microsoft Azure", "category": "Cloud", "aliases": ["azure", "azure cloud"]},
    {"skill_id": "cloud_gcp", "canonical_name": "Google Cloud Platform", "category": "Cloud", "aliases": ["gcp", "google cloud"]},

    # --- DevOps ---
    {"skill_id": "devops_docker", "canonical_name": "Docker", "category": "DevOps", "aliases": []},
    {"skill_id": "devops_k8s", "canonical_name": "Kubernetes", "category": "DevOps", "aliases": ["k8s"]},
    {"skill_id": "devops_terraform", "canonical_name": "Terraform", "category": "DevOps", "aliases": []},
    {"skill_id": "devops_jenkins", "canonical_name": "Jenkins", "category": "DevOps", "aliases": []},
    {"skill_id": "devops_gha", "canonical_name": "GitHub Actions", "category": "DevOps", "aliases": ["github action"]},
    {"skill_id": "devops_cicd", "canonical_name": "CI/CD", "category": "DevOps", "aliases": ["ci cd", "ci/cd pipelines", "continuous integration"]},

    # --- AI / ML ---
    {"skill_id": "ai_ml", "canonical_name": "Machine Learning", "category": "AI / ML", "aliases": ["ml"]},
    {"skill_id": "ai_dl", "canonical_name": "Deep Learning", "category": "AI / ML", "aliases": ["dl"]},
    {"skill_id": "ai_tf", "canonical_name": "TensorFlow", "category": "AI / ML", "aliases": ["tensor flow"]},
    {"skill_id": "ai_pytorch", "canonical_name": "PyTorch", "category": "AI / ML", "aliases": ["py torch"]},
    {"skill_id": "ai_sklearn", "canonical_name": "Scikit-learn", "category": "AI / ML", "aliases": ["scikit learn", "sklearn"]},
    {"skill_id": "ai_llm", "canonical_name": "Large Language Models", "category": "AI / ML", "aliases": ["llm", "llms"]},
    {"skill_id": "ai_genai", "canonical_name": "Generative AI", "category": "AI / ML", "aliases": ["genai", "gen ai"]},
    {"skill_id": "ai_nlp", "canonical_name": "Natural Language Processing", "category": "AI / ML", "aliases": ["nlp"]},
    {"skill_id": "ai_cv", "canonical_name": "Computer Vision", "category": "AI / ML", "aliases": ["cv"]},

    # --- Cybersecurity ---
    {"skill_id": "sec_cyber", "canonical_name": "Cybersecurity", "category": "Cybersecurity", "aliases": ["cyber security", "info sec", "information security"]},
    {"skill_id": "sec_siem", "canonical_name": "SIEM", "category": "Cybersecurity", "aliases": ["splunk", "qradar"]},
    {"skill_id": "sec_iam", "canonical_name": "IAM", "category": "Cybersecurity", "aliases": ["identity and access management", "active directory", "okta"]},
    {"skill_id": "sec_pentest", "canonical_name": "Penetration Testing", "category": "Cybersecurity", "aliases": ["pen testing", "pentesting", "ethical hacking"]},
    {"skill_id": "sec_owasp", "canonical_name": "OWASP", "category": "Cybersecurity", "aliases": []},

    # --- Analytics / BI ---
    {"skill_id": "bi_powerbi", "canonical_name": "Power BI", "category": "Analytics / BI", "aliases": ["powerbi"]},
    {"skill_id": "bi_tableau", "canonical_name": "Tableau", "category": "Analytics / BI", "aliases": []},
    {"skill_id": "bi_excel", "canonical_name": "Excel", "category": "Analytics / BI", "aliases": ["ms excel"]},
    {"skill_id": "bi_looker", "canonical_name": "Looker", "category": "Analytics / BI", "aliases": []},
]
