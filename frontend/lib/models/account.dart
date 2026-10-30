class Account {
  const Account({
    required this.id,
    required this.username,
    required this.email,
  });
  factory Account.fromJson(Map<String, dynamic> json) => Account(
    id: json['id'] as int,
    username: json['username'] as String,
    email: json['email'] as String,
  );
  final int id;
  final String username;
  final String email;
}
