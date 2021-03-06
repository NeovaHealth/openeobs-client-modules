import copy

from openerp.addons.nh_eobs_slam_policy.tests\
    .nh_clinical_patient_observation_ews.test_no_risk import \
    TestNoClinicalRiskPatientAdmittedSevenOrMoreDaysAgo as sevenplusdays
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestSelectFrequencyIsValid(sevenplusdays):
    """
    Test that on:
    1. Submitting a no risk NEWS for a patient with a spell older than 7 days
    2. Completing the triggered assess patient task
    3. Not completing the triggered Review Frequency task
    4. Submitting another NEWS
    5. The original Review Frequency task is considered invalid
    """

    def setUp(self):
        super(TestSelectFrequencyIsValid, self).setUp()
        activity_model = self.env['nh.activity']
        self.frequency_notification = \
            activity_model.browse(self.triggered_ids[0]).data_ref
        self.first_ews_activity_id = self.ews_activity_id
        ews_activity_search = self.activity_pool.search(
            self.cr,
            self.uid,
            [
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['patient_id', '=', self.patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if ews_activity_search:
            self.ews_activity_id = ews_activity_search[0]

    def test_valid_task(self):
        """
        Test that without completing another NEWS observation that the
        notification is considered valid
        """
        self.assertTrue(self.frequency_notification.is_valid())

    def test_validity_after_no_risk(self):
        """
        Test that after completing a new NEWS observation with no clinical
        risk that the notification is considered invalid
        """
        self.complete_obs(clinical_risk_sample_data.NO_RISK_DATA)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_low_risk(self):
        """
        Test that after completing a new NEWS observation with low clinical
        risk that the notification is considered invalid
        """
        self.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_medium_risk(self):
        """
        Test that after completing a new NEWS observation with medium clinical
        risk that the notification is considered invalid
        """
        self.complete_obs(clinical_risk_sample_data.MEDIUM_RISK_DATA)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_high_risk(self):
        """
        Test that after completing a new NEWS observation with high clinical
        risk that the notification is considered invalid
        """
        self.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
        self.assertFalse(self.frequency_notification.is_valid())

    def test_validity_after_partial_obs(self):
        """
        Test that after completing a partial observation that the notification
        isn't considered invalid
        """
        obs = copy.deepcopy(clinical_risk_sample_data.NO_RISK_DATA)
        del obs['respiration_rate']
        obs['partial_reason'] = 'asleep'
        self.complete_obs(obs)
        self.assertTrue(self.frequency_notification.is_valid())
