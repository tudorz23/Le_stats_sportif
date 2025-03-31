"""
Module that manages the dataset used by the server for statistics and the
various operations applied on it.
"""

import csv
import numpy as np

class DataIngestor:
    """
    Data manager.
    """
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
        """
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


    def helper_state_mean(self, question, state):
        """
        Computes the mean of values for given state, regarding given question
        Helper for other compute_ methods.
        """
        state_values = []
        for values in self.database[question][state].values():
            state_values.extend(values)

        return np.average(state_values)


    def helper_states_mean(self, question):
        """
        Computes the mean of values of each state, regarding given question,
        and returns as unsorted dict.
        Helper for other compute_ methods.
        """
        states_mean_dict = {}

        for state, details in self.database[question].items():
            # details <=> [(strat_combo1, [vals]), (strat_combo2, [vals2]), ...]
            state_wide_values = []
            for vals in details.values():
                state_wide_values.extend(vals)

            states_mean_dict[state] = np.average(state_wide_values)

        return states_mean_dict


    def helper_global_mean(self, question):
        """
        Computes the global mean of values, regarding given question.
        Helper for other compute_ methods.
        """
        global_values = []
        for _, details in self.database[question].items():
            # details <=> [(strat_combo1, [vals]), (strat_combo2, [vals2]), ...]
            for vals in details.values():
                global_values.extend(vals)

        return np.average(global_values)


    def compute_states_mean(self, question):
        """
        Computes the mean of values of each state, regarding given question,
        and sorts ascending by mean.
        """
        states_mean_dict = self.helper_states_mean(question)

        return dict(sorted(states_mean_dict.items(), key=lambda item: item[1]))


    def compute_state_mean(self, question, state):
        """
        Computes the mean of values of requested state, regarding given question.
        """
        state_mean = self.helper_state_mean(question, state)
        return {state : state_mean}


    def compute_best5(self, question):
        """
        Computes the mean of values of each state, regarding given question,
        and returns the best 5, according to the question type.
        """
        states_mean_dict = self.helper_states_mean(question)
        rev = question in self.questions_best_is_max

        return dict(sorted(states_mean_dict.items(), key=lambda item: item[1], reverse=rev)[:5])


    def compute_worst5(self, question):
        """
        Computes the mean of values of each state, regarding given question,
        and returns the worst 5, according to the question type.
        """
        states_mean_dict = self.helper_states_mean(question)
        rev = question in self.questions_best_is_min

        return dict(sorted(states_mean_dict.items(), key=lambda item: item[1], reverse=rev)[:5])


    def compute_global_mean(self, question):
        """
        Computes the global mean of values.
        """
        global_mean = self.helper_global_mean(question)

        return {"global_mean" : global_mean}


    def compute_diff_from_mean(self, question):
        """
        Computes the diff between global mean and each state mean.
        """
        global_mean = self.helper_global_mean(question)
        all_states_diff_dict = {}

        for state in self.database[question].keys():
            state_mean = self.helper_state_mean(question, state)
            all_states_diff_dict[state] = global_mean - state_mean

        return all_states_diff_dict


    def compute_state_diff_from_mean(self, question, state):
        """
        Computes the diff between global mean and given state mean.
        """
        global_mean = self.helper_global_mean(question)
        state_mean = self.helper_state_mean(question, state)

        state_diff = global_mean - state_mean
        return {state : state_diff}


    def compute_mean_by_category(self, question):
        """
        Computes the mean of values for every segment of every state.
        """
        mean_by_cat_dict = {}

        for state in self.database[question].keys():
            for strat_combo, values in self.database[question][state].items():
                # Discard empty stratification
                if strat_combo[0] == "" and strat_combo[1] == "":
                    continue

                strat_name = f"('{state}', '{strat_combo[1]}', '{strat_combo[0]}')"
                mean_by_cat_dict[strat_name] = np.average(values)

        return mean_by_cat_dict


    def compute_state_mean_by_category(self, question, state):
        """
        Computes the mean of values for every segment of given state.
        """
        state_mean_by_cat_dict = {state: {}}

        for strat_combo, values in self.database[question][state].items():
            strat_name = f"('{strat_combo[1]}', '{strat_combo[0]}')"
            state_mean_by_cat_dict[state][strat_name] = np.average(values)

        return state_mean_by_cat_dict
