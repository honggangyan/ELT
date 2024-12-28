/*
=== DBT 宏使用总结 ===

1. 基本概念：
宏(Macro)是可重用的代码块，类似函数，用于生成SQL代码。

2. 基础语法：
{% macro macro_name(param1, param2='默认值') %}
    -- SQL代码
{% endmacro %}

3. 常用示例：

=== 循环语句简单示例 ===

1. 生成多个月份数据:
{% macro generate_months() %}
    {% set months = ['01','02','03','04','05','06'] %}
    {% for month in months %}
        SELECT * FROM sales_{{ month }}
        {{ "UNION ALL" if not loop.last }}
    {% endfor %}
{% endmacro %}

-- 输出:
SELECT * FROM sales_01
UNION ALL
SELECT * FROM sales_02
UNION ALL
SELECT * FROM sales_03
...

2. 生成多个聚合计算:
{% macro calculate_metrics() %}
    {% set metrics = ['sales', 'orders', 'customers'] %}
    SELECT 
        date,
        {% for metric in metrics %}
            sum({{ metric }}) as total_{{ metric }}
            {{ "," if not loop.last }}
        {% endfor %}
    FROM daily_stats
{% endmacro %}

-- 输出:
SELECT 
    date,
    sum(sales) as total_sales,
    sum(orders) as total_orders,
    sum(customers) as total_customers
FROM daily_stats

3. 生成简单的CASE语句:
{% macro status_mapping() %}
    {% set status = {
        'A': 'Active',
        'I': 'Inactive',
        'P': 'Pending'
    } %}
    CASE status
    {% for key, value in status.items() %}
        WHEN '{{ key }}' THEN '{{ value }}'
    {% endfor %}
    END
{% endmacro %}

-- 输出:
CASE status
    WHEN 'A' THEN 'Active'
    WHEN 'I' THEN 'Inactive'
    WHEN 'P' THEN 'Pending'
END

4. 生成多个列名:
{% macro select_columns() %}
    {% set columns = ['id', 'name', 'age'] %}
    SELECT 
    {% for col in columns %}
        {{ col }}{{ "," if not loop.last }}
    {% endfor %}
    FROM users
{% endmacro %}

-- 输出:
SELECT 
    id,
    name,
    age
FROM users

使用提示：
1. loop.last 用于判断是否需要添加逗号或UNION ALL
2. 可以使用简单的列表或字典来存储循环项
3. 保持循环逻辑简单清晰
4. 适当添加空格和换行提高可读性
*/


{% macro generate_film_ratings() %}
    WITH film_with_ratings AS (
    SELECT
        f.film_id,
        f.title,
        f.release_date,
        f.price,
        f.rating,
        f.user_rating,
        CASE 
            WHEN f.user_rating >= 4.5 THEN 'Excellent'
            WHEN f.user_rating >= 4.0 THEN 'Good'
            WHEN f.user_rating >= 3.0 THEN 'Average'
            ELSE 'Poor'
        END AS rating_category
    FROM {{ ref('films_view') }} f
),

films_with_actors AS (
    SELECT
        f.film_id,
        f.title,
        STRING_AGG(a.actor_name, ', ') AS actors
    FROM {{ ref('films_view') }} f
    LEFT JOIN {{ ref('film_actors_view') }} fa ON f.film_id = fa.film_id
    LEFT JOIN {{ ref('actors_view') }} a ON fa.actor_id = a.actor_id
    GROUP BY f.film_id, f.title
)

SELECT 
    fwr.*,
    fwa.actors
FROM film_with_ratings fwr
LEFT JOIN films_with_actors fwa ON fwr.film_id = fwa.film_id
ORDER BY fwr.film_id
{% endmacro %}

/*
=== 当前宏使用说明 ===

功能说明:
1. 评分分类转换:
   - Excellent: 用户评分 >= 4.5
   - Good: 用户评分 >= 4.0
   - Average: 用户评分 >= 3.0
   - Poor: 用户评分 < 3.0

2. 数据关联:
   - 关联电影基础信息
   - 关联演员信息（通过 film_actors 和 actors 表）
   - 生成以逗号分隔的演员列表

使用方法:
在模型文件中调用:
{{ generate_film_ratings() }}

依赖模型:
- films
- film_actors
- actors

输出字段:
- film_id: 电影ID
- title: 电影标题
- release_date: 发布日期
- price: 价格
- rating: 原始评分
- user_rating: 用户评分
- rating_category: 评分分类
- actors: 演员列表（逗号分隔）
*/