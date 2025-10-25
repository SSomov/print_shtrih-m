import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/product.dart';

class ApiService {
  // Замените на ваш адрес сервера
  static const String baseUrl = 'http://localhost:8000';
  
  // Получить список категорий
  static Future<List<Category>> getCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/categories'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success') {
          final categoriesJson = data['data'] as List;
          return categoriesJson.map((json) => Category.fromJson(json)).toList();
        }
      }
      throw Exception('Failed to load categories');
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Получить список товаров
  static Future<Map<String, dynamic>> getProducts({
    int? categoryId,
    String? search,
    int page = 1,
    int limit = 100,
  }) async {
    try {
      Uri uri = Uri.parse('$baseUrl/api/v1/products');
      
      Map<String, String> queryParams = {
        'page': page.toString(),
        'limit': limit.toString(),
      };
      
      if (categoryId != null) {
        queryParams['category_id'] = categoryId.toString();
      }
      
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      
      uri = uri.replace(queryParameters: queryParams);
      
      final response = await http.get(uri);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success') {
          final productsJson = data['data'] as List;
          final products = productsJson
              .map((json) => Product.fromJson(json))
              .toList();
          
          return {
            'products': products,
            'pagination': data['pagination'],
          };
        }
      }
      throw Exception('Failed to load products');
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Получить товар по ID
  static Future<Product> getProduct(int productId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/products/$productId'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success') {
          return Product.fromJson(data['data']);
        }
      }
      throw Exception('Failed to load product');
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
}
