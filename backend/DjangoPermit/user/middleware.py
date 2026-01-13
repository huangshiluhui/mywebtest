from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 所有 JWT 相关的导入都移到函数内部
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from jwt import ExpiredSignatureError, PyJWTError
        
        white_list = ["/user/login/"]
        path = request.path
        if path not in white_list and not path.startswith("/media"):
            print("要进行token验证")
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            print("Authorization header:", auth_header)
            
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            
            if not token:
                return HttpResponse('缺少 Token，请先登录！', status=401)
            
            print("提取的 token:", token[:20] + '...' if len(token) > 20 else token)
            
            try:
                # 使用 UntypedToken 验证 token
                UntypedToken(token)
                print("Token 验证成功")
            except ExpiredSignatureError:
                return HttpResponse('Token过期，请重新登录！', status=401)
            except (InvalidToken, TokenError):
                return HttpResponse('Token验证失败！', status=401)
            except PyJWTError as e:
                return HttpResponse(f'Token验证异常：{str(e)}', status=401)
        else:
            print("不需要token验证")
            return None