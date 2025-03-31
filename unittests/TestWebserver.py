"""
Module for unit-testing the DataIngestor class' methods.
"""
import unittest
from app.data_ingestor import DataIngestor
from deepdiff import DeepDiff

class TestWebserver(unittest.TestCase):
    def setUp(self):
        self.data_ingestor = DataIngestor('unittests/data_subset.csv')
        self.question = "Percent of adults aged 18 years and older who have obesity"


    def test_compute_states_mean(self):
        result = self.data_ingestor.compute_states_mean(self.question)
        reference = { "Alaska" : 23.3, "Oregon" : 32.4,
                      "Missouri" : 32.7, "Nevada" : 34.6,
                      "Texas" : 36.3, "Mississippi" : 42.3 }

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_state_mean(self):
        result = self.data_ingestor.compute_state_mean(self.question, "Missouri")
        reference = {"Missouri" : 32.7}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_best5(self):
        result = self.data_ingestor.compute_best5(self.question)
        reference = {"Alaska": 23.3, "Oregon": 32.4, "Missouri": 32.7,
                     "Nevada": 34.6, "Texas": 36.3}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_worst5(self):
        result = self.data_ingestor.compute_worst5(self.question)
        reference = {"Oregon": 32.4, "Missouri": 32.7, "Nevada": 34.6,
                     "Texas": 36.3, "Mississippi": 42.3}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_global_mean(self):
        result = self.data_ingestor.compute_global_mean(self.question)
        reference = {"global_mean" : 34.23}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_diff_from_mean(self):
        result = self.data_ingestor.compute_diff_from_mean(self.question)
        reference = {"Alaska": 10.93, "Oregon": 1.83,
                     "Missouri": 1.53, "Nevada": -0.36,
                     "Texas": -2.06, "Mississippi": -8.06}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_state_diff_from_mean(self):
        result = self.data_ingestor.compute_state_diff_from_mean(self.question, "Missouri")
        reference = {"Missouri": 1.53}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_mean_by_category(self):
        result = self.data_ingestor.compute_mean_by_category(self.question)
        reference = {"('Alaska', 'Race/Ethnicity', '2 or more races')": 23.3,
                     "('Nevada', 'Income', '$25,000 - $34,999')": 34.6,
                     "('Missouri', 'Income', '$75,000 or greater')": 34.5,
                     "('Missouri', 'Race/Ethnicity', 'Hispanic')": 39.6,
                     "('Missouri', 'Race/Ethnicity', 'Non-Hispanic White')": 34.0,
                     "('Missouri', 'Income', '$25,000 - $34,999')": 38.4,
                     "('Missouri', 'Education', 'Less than high school')": 35.0,
                     "('Missouri', 'Race/Ethnicity', 'Asian')": 10.8,
                     "('Missouri', 'Education', 'College graduate')": 28.2,
                     "('Missouri', 'Income', '$50,000 - $74,999')": 35.4,
                     "('Mississippi', 'Income', '$15,000 - $24,999')": 42.4,
                     "('Mississippi', 'Age (years)', '45 - 54')": 49.0,
                     "('Mississippi', 'Income', '$75,000 or greater')": 35.5,
                     "('Texas', 'Race/Ethnicity', 'Non-Hispanic Black')": 36.3,
                     "('Oregon', 'Income', '$50,000 - $74,999')": 32.4}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)

    def test_compute_state_mean_by_category(self):
        result = self.data_ingestor.compute_state_mean_by_category(self.question, "Missouri")
        reference = {"Missouri" : {"('Income', '$75,000 or greater')": 34.5,
                     "('Race/Ethnicity', 'Hispanic')": 39.6,
                     "('Race/Ethnicity', 'Non-Hispanic White')": 34.0,
                     "('Income', '$25,000 - $34,999')": 38.4,
                     "('Education', 'Less than high school')": 35.0,
                     "('Race/Ethnicity', 'Asian')": 10.8,
                     "('Education', 'College graduate')": 28.2,
                     "('Income', '$50,000 - $74,999')": 35.4}}

        diff = DeepDiff(result, reference, math_epsilon=0.01)
        self.assertTrue(not diff)
