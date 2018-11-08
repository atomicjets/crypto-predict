import unittest
from dotenv import find_dotenv, load_dotenv
import os
from sklearn.model_selection import train_test_split
import datetime
from crypr.data.cryptocompare import retrieve_all_data
from crypr.features.build import *
from crypr.base.models import RegressionModel, SavedRegressionModel
from crypr.base.preprocessors import SimplePreprocessor
from xgboost import XGBRegressor

class TestInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # print('setupClass')
        pass

    @classmethod
    def tearDownClass(cls):
        # print('teardownClass')
        pass

    def setUp(self):
        print('setUp')
        np.random.seed(31337)

        load_dotenv(find_dotenv())
        self.project_path = os.path.dirname(find_dotenv())

        self.SYM = 'ETH'
        LAST_N_HOURS = 16000
        self.FEATURE_WINDOW=72
        self.MOVING_AVERAGE_LAGS = [6, 12, 24, 48, 72]
        self.TARGET = 'close'
        self.Tx = 72
        self.Ty = 1
        self.TEST_SIZE = 0.05

        self.data = retrieve_all_data(coin=self.SYM, num_hours=LAST_N_HOURS, comparison_symbol='USD',
                                 end_time=(np.datetime64(datetime.datetime(2018,6,27)).astype('uint64') / 1e6).astype('uint32'))

        self.predict_data = retrieve_all_data(self.SYM, self.Tx + self.FEATURE_WINDOW - 1,
                                 end_time=(np.datetime64(datetime.datetime(2018, 6, 27)).astype('uint64') / 1e6).astype(
                                 'uint32'))

        self.X_shape =(13859, 1224)
        self.y_shape =(13859, 1)

        self.X_sample = 705.68
        self.y_sample = -0.2896853523991494

        self.X_train_shape =(13166, 1224)
        self.X_test_shape =(693, 1224)
        self.y_train_shape = (13166, 1)
        self.y_test_shape = (693, 1)

        self.X_train_sample = 88.2
        self.y_train_sample = 0.17391304347826875

        self.X_test_sample = 487.58
        self.y_test_sample = 0.9448599618077758

        self.parameters = {
            'objective': 'reg:linear',
            'learning_rate': .07,
            'max_depth': 10,
            'min_child_weight': 4,
            'silent': 1,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'n_estimators': 20
        }

        self.train_mae = 0.8968620419351427
        self.train_rmse = 1.4206723934489915
        # self.test_mae = 0.6681529049518523
        # self.test_rmse = 1.0195120681618908

        self.prediction =  -0.09979289770126343

    def tearDown(self):
        # print('tearDown')
        pass

    def test_preprocess(self):
        np.random.seed(31337)
        preprocessor = SimplePreprocessor(False, self.TARGET, self.Tx, self.Ty, self.MOVING_AVERAGE_LAGS, name='Unit_Test')

        X, y = preprocessor.fit(self.data).transform(self.data)
        X_sample = X.sample(1, random_state=0).values[0][0]
        y_sample = y.sample(1, random_state=0).values[0][0]
        self.assertEqual((X_sample, y_sample, X.shape, y.shape), (self.X_sample, self.y_sample, self.X_shape, self.y_shape))

    def test_split(self):
        np.random.seed(31337)
        preprocessor = SimplePreprocessor(False, self.TARGET, self.Tx, self.Ty, self.MOVING_AVERAGE_LAGS,
                                          name='Unit_Test')
        X, y = preprocessor.fit(self.data).transform(self.data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.TEST_SIZE, shuffle=False)
        X_train_sample=X_train.sample(1, random_state=0).values[0][0]
        X_test_sample=X_test.sample(1, random_state=0).values[0][0]
        y_train_sample=y_train.sample(1, random_state=0).values[0][0]
        y_test_sample=y_test.sample(1, random_state=0).values[0][0]
        self.assertEqual((X_train_sample, X_test_sample, y_train_sample, y_test_sample,
                          X_train.shape, X_test.shape, y_train.shape, y_test.shape),
                         (self.X_train_sample, self.X_test_sample, self.y_train_sample, self.y_test_sample,
                          self.X_train_shape, self.X_test_shape, self.y_train_shape, self.y_test_shape))

    def test_fit(self):
        np.random.seed(31337)
        preprocessor = SimplePreprocessor(False, self.TARGET, self.Tx, self.Ty, self.MOVING_AVERAGE_LAGS, name='Unit_Test')

        X, y = preprocessor.fit(self.data).transform(self.data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.TEST_SIZE, shuffle=False)
        self.ta = RegressionModel(XGBRegressor(), 'Unit_Test_Regressor')

        self.ta.estimator.set_params(**self.parameters)
        self.ta.fit(X_train, y_train)
        train_pred = self.ta.predict(X_train)
        rmse, mae = self.ta.evaluate(y_pred=train_pred, y_true=y_train)
        self.assertAlmostEqual(rmse, self.train_rmse, 2)
        self.assertAlmostEqual(mae, self.train_mae, 2)

    def test_predict(self):
        np.random.seed(31337)
        preprocessor = SimplePreprocessor(True, self.TARGET, self.Tx, self.Ty, self.MOVING_AVERAGE_LAGS, name='Unit_Test')
        X = preprocessor.fit(self.predict_data).transform(self.predict_data)
        self.ta = SavedRegressionModel('{}/unit_xgboost_ETH_tx72_ty1_flag72.pkl'.format(self.project_path))
        self.assertEqual(self.ta.predict(X)[0], self.prediction)


if __name__ == '__main__':

    # run tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)