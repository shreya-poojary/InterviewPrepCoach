"""
Database schema - SQL statements for creating all tables
"""

CREATE_DATABASE = """
CREATE DATABASE IF NOT EXISTS interview_prep_ai 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
"""

CREATE_TABLES = [
    # Users table
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_email (email),
        INDEX idx_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # User profiles table
    """
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        full_name VARCHAR(255),
        phone VARCHAR(50),
        location VARCHAR(255),
        linkedin_url VARCHAR(500),
        github_url VARCHAR(500),
        portfolio_url VARCHAR(500),
        target_role VARCHAR(255),
        target_industry VARCHAR(255),
        years_experience INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Resumes table
    """
    CREATE TABLE IF NOT EXISTS resumes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_type VARCHAR(50),
        file_size INT,
        extracted_text LONGTEXT,
        parsed_data JSON,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Job descriptions table
    """
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        location VARCHAR(255),
        salary_range VARCHAR(100),
        description_text LONGTEXT NOT NULL,
        requirements LONGTEXT,
        parsed_data JSON,
        source VARCHAR(100),
        source_url VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_company (company)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Compatibility analyses table
    """
    CREATE TABLE IF NOT EXISTS compatibility_analyses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        resume_id INT NOT NULL,
        job_description_id INT NOT NULL,
        compatibility_score DECIMAL(5,2),
        matched_skills JSON,
        missing_skills JSON,
        missing_qualifications JSON,
        strengths JSON,
        suggestions LONGTEXT,
        analysis_data JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_score (compatibility_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Question sets table
    """
    CREATE TABLE IF NOT EXISTS question_sets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        job_description_id INT,
        resume_id INT,
        difficulty_level ENUM('easy', 'medium', 'hard', 'mixed') DEFAULT 'mixed',
        question_count INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE SET NULL,
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Questions table
    """
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question_set_id INT NOT NULL,
        question_text LONGTEXT NOT NULL,
        question_type ENUM('behavioral', 'technical', 'situational', 'case_study') NOT NULL,
        difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
        ideal_answer_points LONGTEXT,
        evaluation_criteria JSON,
        tags JSON,
        order_index INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_set_id) REFERENCES question_sets(id) ON DELETE CASCADE,
        INDEX idx_question_set_id (question_set_id),
        INDEX idx_type (question_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Practice sessions table
    """
    CREATE TABLE IF NOT EXISTS practice_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question_set_id INT,
        session_type ENUM('written', 'audio', 'video') NOT NULL,
        status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
        total_questions INT DEFAULT 0,
        answered_questions INT DEFAULT 0,
        average_score DECIMAL(5,2),
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP NULL,
        duration_seconds INT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (question_set_id) REFERENCES question_sets(id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Practice responses table
    """
    CREATE TABLE IF NOT EXISTS practice_responses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        question_id INT NOT NULL,
        response_text LONGTEXT,
        audio_file_path VARCHAR(500),
        video_file_path VARCHAR(500),
        transcription LONGTEXT,
        ai_score DECIMAL(5,2),
        ai_feedback LONGTEXT,
        evaluation_data JSON,
        time_taken_seconds INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
        INDEX idx_session_id (session_id),
        INDEX idx_question_id (question_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Applications table
    """
    CREATE TABLE IF NOT EXISTS applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        job_description_id INT,
        company VARCHAR(255) NOT NULL,
        position VARCHAR(255) NOT NULL,
        location VARCHAR(255),
        application_date DATE NOT NULL,
        status ENUM('applied', 'phone_screen', 'technical_interview', 
                    'onsite_interview', 'offer_received', 'rejected', 'withdrawn') 
                DEFAULT 'applied',
        job_url VARCHAR(500),
        salary_expectation VARCHAR(100),
        notes LONGTEXT,
        resume_used INT,
        cover_letter_used INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_application_date (application_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Application reminders table
    """
    CREATE TABLE IF NOT EXISTS application_reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        application_id INT NOT NULL,
        reminder_date DATE NOT NULL,
        reminder_type ENUM('follow_up', 'interview', 'deadline', 'other') NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        is_completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
        INDEX idx_application_id (application_id),
        INDEX idx_reminder_date (reminder_date),
        INDEX idx_is_completed (is_completed)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Generated documents table
    """
    CREATE TABLE IF NOT EXISTS generated_documents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        document_type ENUM('resume', 'cover_letter', 'cold_email', 'thank_you', 'other') NOT NULL,
        title VARCHAR(255) NOT NULL,
        content LONGTEXT NOT NULL,
        file_path VARCHAR(500),
        template_used VARCHAR(100),
        job_description_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_document_type (document_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Coach conversations table
    """
    CREATE TABLE IF NOT EXISTS coach_conversations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255),
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        message_count INT DEFAULT 0,
        is_archived BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_last_message_at (last_message_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # Coach messages table
    """
    CREATE TABLE IF NOT EXISTS coach_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        conversation_id INT NOT NULL,
        role ENUM('user', 'assistant', 'system') NOT NULL,
        content LONGTEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES coach_conversations(id) ON DELETE CASCADE,
        INDEX idx_conversation_id (conversation_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # JSearch jobs table
    """
    CREATE TABLE IF NOT EXISTS jsearch_jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        job_id VARCHAR(255) UNIQUE,
        title VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        location VARCHAR(255),
        description LONGTEXT,
        salary_min DECIMAL(12,2),
        salary_max DECIMAL(12,2),
        is_remote BOOLEAN DEFAULT FALSE,
        job_url VARCHAR(500),
        apply_url VARCHAR(500),
        posted_date DATE,
        job_data JSON,
        compatibility_score DECIMAL(5,2),
        is_saved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_job_id (job_id),
        INDEX idx_is_saved (is_saved),
        INDEX idx_compatibility_score (compatibility_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # JSearch history table
    """
    CREATE TABLE IF NOT EXISTS jsearch_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        search_query VARCHAR(500) NOT NULL,
        location VARCHAR(255),
        remote_only BOOLEAN DEFAULT FALSE,
        results_count INT DEFAULT 0,
        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_searched_at (searched_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    # LLM settings table
    """
    CREATE TABLE IF NOT EXISTS llm_settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        provider ENUM('openai', 'anthropic', 'bedrock', 'ollama') NOT NULL,
        model VARCHAR(100) NOT NULL,
        api_key_encrypted TEXT,
        temperature DECIMAL(3,2) DEFAULT 0.70,
        max_tokens INT DEFAULT 2000,
        additional_config JSON,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

INSERT_DEFAULT_USER = """
INSERT IGNORE INTO users (id, username, email, password_hash) 
VALUES (1, 'default_user', 'user@interviewprep.ai', NULL);
"""
