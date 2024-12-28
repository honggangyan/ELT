/*
文件: film_ratings.sql
用途: 第二层转换 - 基于films模型的评分分析
*/

{{ config(
    materialized='view',
    description='电影评分分析视图，包含评分分类和演员信息'
) }}

-- 使用 Jinja 语法调用宏
{{ generate_film_ratings() }}