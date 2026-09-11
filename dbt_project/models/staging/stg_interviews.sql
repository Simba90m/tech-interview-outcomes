with source as (

    select * from {{ source('raw', 'raw_interviews') }}

),

cleaned as (

    select
        -- The source "ID" column collides for 3 pairs of distinct candidates
        -- (different names/roles/decisions sharing one ID), a real data quality
        -- issue in the source data. row_number() gives a guaranteed-unique key;
        -- the original ID is kept as source_id for traceability.
        row_number() over (order by "ID") as interview_id,
        "ID" as source_id,
        "Name" as candidate_name,
        trim(lower("Role")) as role_norm,
        "Role" as role_raw,
        lower("decision") as decision,
        "Reason_for_decision" as reason_raw,
        "Job_Description" as job_description,
        "Resume" as resume_text,
        "Transcript" as transcript_text,
        length("Resume") - length(replace("Resume", ' ', '')) + 1 as resume_word_count,
        length("Transcript") - length(replace("Transcript", ' ', '')) + 1 as transcript_word_count,

        -- Real data quality finding: ~9.5% of reason values are actually a leaked
        -- job-requirement string ("expected_experience : ... , domains: ...")
        -- rather than a genuine decision reason.
        (lower("Reason_for_decision") like '%expected_experience%') as is_requirement_leak,

        case
            when lower("Reason_for_decision") like '%expected_experience%'
                then 'Data Quality: Requirement Text Leaked'

            when lower("Reason_for_decision") like '%problem-solving%'
                or lower("Reason_for_decision") like '%problem solving%'
                then 'Problem Solving'

            when lower("Reason_for_decision") like '%reference%'
                or lower("Reason_for_decision") like '%background check%'
                then 'Background / References'

            when lower("Reason_for_decision") like '%leadership%'
                or lower("Reason_for_decision") like '%communicat%'
                or lower("Reason_for_decision") like '%interpersonal%'
                or lower("Reason_for_decision") like '%collaboration%'
                or lower("Reason_for_decision") like '%teamwork%'
                or lower("Reason_for_decision") like '%curiosity%'
                or lower("Reason_for_decision") like '%initiative%'
                or lower("Reason_for_decision") like '%rigidity%'
                or lower("Reason_for_decision") like '%preparedness%'
                or lower("Reason_for_decision") like '%theoretical knowledge%'
                then 'Leadership & Communication'

            when lower("Reason_for_decision") like '%cultural fit%'
                or lower("Reason_for_decision") like '%adapt%'
                or lower("Reason_for_decision") like '%enthusiasm%'
                or lower("Reason_for_decision") like '%growth mindset%'
                or lower("Reason_for_decision") like '%remote work%'
                then 'Culture & Adaptability'

            when lower("Reason_for_decision") like '%technical%'
                or lower("Reason_for_decision") like '%system design%'
                or lower("Reason_for_decision") like '%back-end%'
                or lower("Reason_for_decision") like '%full-stack%'
                or lower("Reason_for_decision") like '%machine learning%'
                or lower("Reason_for_decision") like '%cloud platform%'
                or lower("Reason_for_decision") like '%code solutions%'
                or lower("Reason_for_decision") like '%data engineering%'
                or lower("Reason_for_decision") like '%expertise in required domains%'
                or lower("Reason_for_decision") like '%innovative%'
                or lower("Reason_for_decision") like '%creative solutions%'
                or lower("Reason_for_decision") like '%company%goals%'
                or lower("Reason_for_decision") like '%insufficient mastery%'
                or lower("Reason_for_decision") like '%lacks sufficient expertise%'
                or lower("Reason_for_decision") like '%crucial technical skills%'
                then 'Technical Skills'

            when lower("Reason_for_decision") like '%business acumen%'
                or lower("Reason_for_decision") like '%experience%'
                or lower("Reason_for_decision") like '%track record%'
                or lower("Reason_for_decision") like '%relevant skills%'
                or lower("Reason_for_decision") like '%domains%'
                or lower("Reason_for_decision") like '%unsuitable%'
                then 'Experience & Domain Fit'

            else 'Other / Unspecified'
        end as reason_category

    from source

)

select * from cleaned
