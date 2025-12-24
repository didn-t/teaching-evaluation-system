"""
完整的API接口测试脚本
包含使用真实测试数据的测试
"""
import asyncio
import httpx
import json
from datetime import datetime


class CompleteAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None

    async def test_health_endpoints(self):
        """测试健康检查端点"""
        print("1. 测试健康检查端点")
        
        # 测试基础健康检查
        try:
            response = await self.client.get(f"{self.base_url}/health")
            print(f"   健康检查状态: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   健康检查异常: {e}")
        
        # 测试数据库健康检查
        try:
            response = await self.client.get(f"{self.base_url}/health/db")
            print(f"   数据库健康检查状态: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   数据库健康检查异常: {e}")

    async def test_user_login(self, user_no: str, password: str):
        """测试用户登录"""
        print(f"\n2. 测试用户登录 - 账号: {user_no}")
        
        login_data = {
            "user_no": user_no,
            "password": password
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/teaching-eval/user/login",
                json=login_data
            )
            print(f"   登录响应状态: {response.status_code}")
            print(f"   登录响应: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    self.access_token = result["data"]["access_token"]
                    print(f"   登录成功！获取到token: {self.access_token[:20]}...")
                    return True
                else:
                    print(f"   登录失败: {result.get('msg', '未知错误')}")
            else:
                print(f"   登录请求失败")
                
        except Exception as e:
            print(f"   登录请求异常: {e}")
        
        return False

    async def test_protected_endpoints(self):
        """测试需要认证的端点（如果已登录）"""
        if not self.access_token:
            print("\n3. 跳过需要认证的端点测试（未登录）")
            return
        
        print(f"\n3. 测试需要认证的端点")
        
        # 设置认证头
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            # 测试用户信息端点
            response = await self.client.get(
                f"{self.base_url}/api/v1/teaching-eval/user/info",
                headers=headers
            )
            print(f"   用户信息端点状态: {response.status_code}")
            print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   用户信息端点异常: {e}")

    async def test_api_documentation(self):
        """测试API文档端点"""
        print(f"\n4. 测试API文档端点")
        
        endpoints = ["/docs", "/redoc"]
        for endpoint in endpoints:
            try:
                response = await self.client.get(f"{self.base_url}{endpoint}")
                print(f"   {endpoint} 状态: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint} 异常: {e}")

    async def run_complete_test(self):
        """运行完整测试"""
        print("=" * 70)
        print("开始运行完整API测试")
        print(f"目标URL: {self.base_url}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 测试健康检查
        await self.test_health_endpoints()
        
        # 测试不同用户的登录
        test_users = [
            ("admin", "admin123"),
            ("teacher001", "teacher123"),
            ("supervisor001", "supervisor123"),
            ("invalid_user", "invalid_password")  # 测试无效用户
        ]
        
        for user_no, password in test_users:
            await self.test_user_login(user_no, password)
            # 短暂延迟以避免请求过快
            await asyncio.sleep(0.5)
        
        # 测试需要认证的端点
        await self.test_protected_endpoints()
        
        # 测试API文档
        await self.test_api_documentation()
        
        print("\n" + "=" * 70)
        print("完整API测试完成")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.access_token:
            print("注意: 已获取认证token，可继续进行其他测试")
        print("=" * 70)

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    tester = CompleteAPITester(base_url="http://localhost:8000")
    
    try:
        await tester.run_complete_test()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())