class Product {
  final int id;
  final String name;
  final String? description;
  final Category category;
  final double price;
  final String? barcode;
  final String? legacyPath;
  final String unit;
  final double maxDiscount;
  final double taxRate;
  final bool isAlcohol;
  final bool isMarked;
  final bool isDraught;
  final bool isBottled;
  final String? alcCode;
  final String? egaisMarkCode;
  final String? egaisId;
  final String? gtin;

  Product({
    required this.id,
    required this.name,
    this.description,
    required this.category,
    required this.price,
    this.barcode,
    this.legacyPath,
    required this.unit,
    required this.maxDiscount,
    required this.taxRate,
    required this.isAlcohol,
    required this.isMarked,
    required this.isDraught,
    required this.isBottled,
    this.alcCode,
    this.egaisMarkCode,
    this.egaisId,
    this.gtin,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      category: Category.fromJson(json['category']),
      price: (json['price'] as num).toDouble(),
      barcode: json['barcode'],
      legacyPath: json['legacy_path'],
      unit: json['unit'],
      maxDiscount: (json['max_discount'] as num).toDouble(),
      taxRate: (json['tax_rate'] as num).toDouble(),
      isAlcohol: json['is_alcohol'],
      isMarked: json['is_marked'],
      isDraught: json['is_draught'],
      isBottled: json['is_bottled'],
      alcCode: json['alc_code'],
      egaisMarkCode: json['egais_mark_code'],
      egaisId: json['egais_id'],
      gtin: json['gtin'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'category': category.toJson(),
      'price': price,
      'barcode': barcode,
      'legacy_path': legacyPath,
      'unit': unit,
      'max_discount': maxDiscount,
      'tax_rate': taxRate,
      'is_alcohol': isAlcohol,
      'is_marked': isMarked,
      'is_draught': isDraught,
      'is_bottled': isBottled,
      'alc_code': alcCode,
      'egais_mark_code': egaisMarkCode,
      'egais_id': egaisId,
      'gtin': gtin,
    };
  }
}

class Category {
  final int id;
  final String name;
  final String? description;

  Category({
    required this.id,
    required this.name,
    this.description,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'],
      description: json['description'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
    };
  }
}
