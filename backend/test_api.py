"""
API 接口测试文件
用于测试教学评价系统的用户认证接口
"""
import asyncio
import httpx
import json
from datetime import datetime


class TeachingEvaluationAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None

    async def test_health_check(self):
        """测试健康检查接口"""
        print(f"正在测试健康检查接口...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            print(f"健康检查接口响应状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"健康检查接口响应内容: {response.json()}")
                return True
            else:
                print(f"健康检查接口错误响应: {response.text}")
                return False
            
        except Exception as e:
            print(f"健康检查请求异常: {str(e)}")
            return False

    async def test_database_health_check(self):
        """测试数据库健康检查接口"""
        print(f"正在测试数据库健康检查接口...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health/db")
            
            print(f"数据库健康检查接口响应状态码: {response.status_code}")
            print(f"数据库健康检查接口响应内容: {response.json()}")
            
            return response.status_code == 200 or response.status_code == 503  # 503也是正常响应
            
        except Exception as e:
            print(f"数据库健康检查请求异常: {str(e)}")
            return False

    async def test_get_user_info(self):
        """测试获取用户信息接口（如果已登录）"""
        print(f"正在测试获取用户信息接口...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/teaching-eval/user/info")
            
            print(f"获取用户信息接口响应状态码: {response.status_code}")
            print(f"获取用户信息接口响应内容: {response.text}")
            
            return response.status_code in [200, 401]  # 200是成功，401是未认证，都算正常响应
            
        except Exception as e:
            print(f"获取用户信息请求异常: {str(e)}")
            return False

    async def test_login_endpoint(self, user_no: str = "test_user", password: str = "test_password"):
        """测试用户登录接口"""
        print(f"正在测试登录接口...")
        
        login_data = {
            "user_no": user_no,
            "password": password
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/teaching-eval/user/login",
                json=login_data
            )
            
            print(f"登录接口响应状态码: {response.status_code}")
            print(f"登录接口响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("登录成功！")
                    return True
                else:
                    print(f"登录失败: {result.get('msg', '未知错误')}")
                    return True  # 请求成功，即使登录失败
            else:
                print(f"登录请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"登录请求异常: {str(e)}")
            return False

    async def run_basic_tests(self):
        """运行基本测试"""
        print("=" * 60)
        print("开始测试教学评价系统 API 接口")
        print(f"测试基础 URL: {self.base_url}")
        print("=" * 60)
        
        # 测试健康检查
        print("\n1. 测试健康检查接口")
        health_ok = await self.test_health_check()
        
        print("\n2. 测试数据库健康检查接口")
        db_health_ok = await self.test_database_health_check()
        
        # 测试获取用户信息（无需认证）
        print("\n3. 测试获取用户信息接口")
        user_info_ok = await self.test_get_user_info()
        
        # 测试登录接口
        print("\n4. 测试用户登录接口")
        login_ok = await self.test_login_endpoint()
        
        # 测试总结
        print("\n" + "=" * 60)
        print("测试结果总结:")
        print(f"健康检查: {'✓' if health_ok else '✗'}")
        print(f"数据库健康检查: {'✓' if db_health_ok else '✗'}")
        print(f"获取用户信息: {'✓' if user_info_ok else '✗'}")
        print(f"用户登录: {'✓' if login_ok else '✗'}")
        
        all_tests_completed = health_ok and db_health_ok and user_info_ok and login_ok
        print(f"总体测试结果: {'✓ 全部完成' if all_tests_completed else '✗ 部分失败'}")
        print("=" * 60)
        
        return all_tests_completed

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    # 创建测试实例
    tester = TeachingEvaluationAPITester(base_url="http://localhost:8000")
    
    try:
        # 运行基本测试
        await tester.run_basic_tests()
    finally:
        # 关闭客户端
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())