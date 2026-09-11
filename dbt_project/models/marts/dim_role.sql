with interviews as (

    select * from {{ ref('stg_interviews') }}

),

role_family as (

    select * from {{ ref('stg_role_family') }}

),

agg as (

    select
        i.role_norm,
        rf.role_family,
        rf.role_display,
        count(*) as total_interviews,
        sum(case when i.decision = 'select' then 1 else 0 end) as total_selected,
        round(
            100.0 * sum(case when i.decision = 'select' then 1 else 0 end) / count(*),
            1
        ) as selection_rate_pct
    from interviews i
    left join role_family rf on i.role_norm = rf.role_norm
    group by 1, 2, 3

)

select * from agg
