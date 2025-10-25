import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  // Замените на ваш адрес сервера
  static const String baseUrl = 'http://localhost:8000';
  static const storage = FlutterSecureStorage();
  static const String _tokenKey = 'auth_token';
  static const String _usernameKey = 'username';

  // Авторизация
  static Future<AuthResult> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success') {
          final token = data['token'];
          final username = data['username'];
          
          // Сохраняем токен и имя пользователя
          await storage.write(key: _tokenKey, value: token);
          await storage.write(key: _usernameKey, value: username);
          
          return AuthResult(
            success: true,
            token: token,
            username: username,
            message: 'Успешная авторизация',
          );
        } else {
          return AuthResult(
            success: false,
            message: data['message'] ?? 'Ошибка авторизации',
          );
        }
      } else {
        final data = json.decode(response.body);
        return AuthResult(
          success: false,
          message: data['message'] ?? 'Ошибка авторизации',
        );
      }
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'Ошибка подключения: $e',
      );
    }
  }

  // Выход
  static Future<void> logout() async {
    await storage.delete(key: _tokenKey);
    await storage.delete(key: _usernameKey);
  }

  // Проверка авторизации
  static Future<bool> isAuthenticated() async {
    final token = await storage.read(key: _tokenKey);
    return token != null && token.isNotEmpty;
  }

  // Получить токен
  static Future<String?> getToken() async {
    return await storage.read(key: _tokenKey);
  }

  // Получить имя пользователя
  static Future<String?> getUsername() async {
    return await storage.read(key: _usernameKey);
  }

  // Получить заголовки с авторизацией
  static Future<Map<String, String>> getAuthHeaders() async {
    final token = await getToken();
    if (token != null) {
      return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };
    }
    return {'Content-Type': 'application/json'};
  }
}

class AuthResult {
  final bool success;
  final String? token;
  final String? username;
  final String message;

  AuthResult({
    required this.success,
    this.token,
    this.username,
    required this.message,
  });
}
