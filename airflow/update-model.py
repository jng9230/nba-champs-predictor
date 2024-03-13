import datetime
import pendulum
import os

import requests
from airflow.decorators import dag, task
# from airflow.providers.postgres.hooks.postgres import PostgresHook
# from airflow.providers.postgres.operators.postgres import PostgresOperator


@dag(
    dag_id="process-employees",
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def UpdateModel():
    @task
    def create_standings_table():
        return

    # Creates a temp table for storing intermediary data
    #   USE CSVs + Panda instead tbh
    # create_standings_table_temp = PostgresOperator()
    @task 
    def create_standings_table_temp():
        return

    @task 
    def get_data():
        return
    
    @task
    def get_old_data():
        return

    @task
    def combine_data():
        return
    
    @task
    def update_model():
        return
    
    @task
    def load_data():
        return
    
    @task
    def update_website():
        return

    return

dag = UpdateModel()