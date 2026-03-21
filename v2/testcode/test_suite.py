import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所有测试模块
from test_basic_functions import TestBasicFunctions
from test_new_features import TestNewFeatures
from test_data_persistence import TestDataPersistence


def run_all_tests():
    """运行所有测试"""
    print("开始运行 v2 版本测试套件...")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例（继承并扩展v1版本的测试）
    suite.addTests(unittest.makeSuite(TestBasicFunctions))
    suite.addTests(unittest.makeSuite(TestNewFeatures))
    suite.addTests(unittest.makeSuite(TestDataPersistence))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n测试结果:")
    print(f"总测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)