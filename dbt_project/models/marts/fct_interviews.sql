with interviews as (

    select * from {{ ref('stg_interviews') }}

),

role_family as (

    select * from {{ ref('stg_role_family') }}

),

final as (

    select
        i.interview_id,
        i.source_id,
        i.candidate_name,
        i.role_norm,
        rf.role_display,
        rf.role_family,
        i.decision,
        i.reason_raw,
        i.reason_category,
        i.is_requirement_leak,
        i.resume_word_count,
        i.transcript_word_count,
        i.job_description
    from interviews i
    left join role_family rf on i.role_norm = rf.role_norm

)

select * from final
