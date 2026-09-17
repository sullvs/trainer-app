CREATE TABLE if not exists users (
    user_id SERIAL primary key, 
    first_name text not null, 
    last_name text not null, 
    password text not null, 
    email text UNIQUE not null, 
    height real, 
    role text not null, 
    birthdate text, 
    registration_date text not null, 
    membership_duration text, 
    membership_start_date text,
    target_weight real);

CREATE TABLE if not exists food_log (
    food_log_id SERIAL primary key , 
    user_id integer references users(user_id), 
    meal_type text, 
    quantity numeric,
    meal_content text, 
    log_time text);

CREATE TABLE if not exists weight_log (
    weight_log_id SERIAL primary key, 
    user_id integer references users(user_id), 
    current_weight real not null, 
    log_time text not null);

CREATE TABLE if not exists workout (
    workout_id SERIAL primary key, 
    user_id integer references users(user_id), 
    num_of_days integer, 
    suitable_workout_split text, 
    log_time text not null);