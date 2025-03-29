import os
import json
import csv

class DataIngestor:
    def __init__(self, csv_path: str):
        self.database = {}

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

        self.populate_database(csv_path)

    def populate_database(self, csv_path: str):
        """"
        Builds the database as a dictionary as follows:
            {question :
                {state :
                    { (strat1, strat_cat1) : [values] }
                }
            }
        """

        # Add the questions to the database
        for question in self.questions_best_is_min:
            self.database[question] = {}

        for question in self.questions_best_is_max:
            self.database[question] = {}

        with open(csv_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for line in csv_reader:
                # Extract relevant data
                question = line["Question"]
                state = line["LocationDesc"]
                strat_combo = (line["Stratification1"], line["StratificationCategory1"])
                value = float(line["Data_Value"])

                if state not in self.database[question]:
                    self.database[question][state] = {}

                if strat_combo not in self.database[question][state]:
                    self.database[question][state][strat_combo] = []

                self.database[question][state][strat_combo].append(value)

    def compute_states_mean(self, question):
        pass

    def compute_state_mean(self, question, state):
        pass

    def compute_best5(self, question):
        pass

    def compute_worst5(self, question):
        pass

    def compute_global_mean(self, question):
        pass

    def compute_diff_from_mean(self, question):
        pass

    def compute_state_diff_from_mean(self, question, state):
        pass

    def compute_mean_by_category(self, question):
        pass

    def compute_state_mean_by_category(self, question, state):
        pass