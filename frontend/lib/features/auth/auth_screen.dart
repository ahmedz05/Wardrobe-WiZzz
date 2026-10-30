import 'dart:convert';

import 'package:flutter/material.dart';

import '../../core/app_theme.dart';
import '../../shared/widgets.dart';
import 'auth_controller.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.auth});
  final AuthController auth;
  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _form = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _register = false;
  bool _visible = false;

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    if (_register) {
      final created = await widget.auth.register(
        _username.text,
        _email.text,
        _password.text,
      );
      if (created && mounted) {
        setState(() {
          _register = false;
          _password.clear();
        });
      }
    } else {
      await widget.auth.signIn(_email.text, _password.text);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final wide =
              constraints.maxWidth >= 900 && constraints.maxHeight >= 700;
          final form = Center(
            child: SingleChildScrollView(
              padding: EdgeInsets.all(wide ? 48 : 24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: AutofillGroup(
                  child: Form(
                    key: _form,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Brand(),
                        const SizedBox(height: 48),
                        Text(
                          _register
                              ? 'Make room for\nyour style.'
                              : 'Good style starts\nwith what you own.',
                          style: Theme.of(context).textTheme.headlineLarge,
                        ),
                        const SizedBox(height: 14),
                        Text(
                          _register
                              ? 'Create your account to bring your wardrobe together.'
                              : 'Sign in to rediscover your wardrobe and find your next outfit.',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                        const SizedBox(height: 28),
                        if (widget.auth.error != null) ...[
                          MessageBox(widget.auth.error!),
                          const SizedBox(height: 18),
                        ],
                        if (widget.auth.notice != null) ...[
                          MessageBox(widget.auth.notice!, isError: false),
                          const SizedBox(height: 18),
                        ],
                        if (_register) ...[
                          TextFormField(
                            key: const Key('username'),
                            controller: _username,
                            enabled: !widget.auth.busy,
                            autofillHints: const [AutofillHints.newUsername],
                            textInputAction: TextInputAction.next,
                            decoration: const InputDecoration(
                              labelText: 'Username',
                              prefixIcon: Icon(Icons.person_outline),
                            ),
                            validator: (value) =>
                                value == null || value.trim().isEmpty
                                ? 'Enter a username.'
                                : null,
                          ),
                          const SizedBox(height: 16),
                        ],
                        TextFormField(
                          key: const Key('email'),
                          controller: _email,
                          enabled: !widget.auth.busy,
                          autofillHints: const [AutofillHints.email],
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          autocorrect: false,
                          enableSuggestions: false,
                          decoration: const InputDecoration(
                            labelText: 'Email address',
                            prefixIcon: Icon(Icons.mail_outline),
                          ),
                          validator: (value) =>
                              value == null ||
                                  !RegExp(
                                    r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
                                  ).hasMatch(value.trim())
                              ? 'Enter a valid email address.'
                              : null,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          key: const Key('password'),
                          controller: _password,
                          enabled: !widget.auth.busy,
                          obscureText: !_visible,
                          autocorrect: false,
                          enableSuggestions: false,
                          autofillHints: [
                            _register
                                ? AutofillHints.newPassword
                                : AutofillHints.password,
                          ],
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) =>
                              widget.auth.busy ? null : _submit(),
                          decoration: InputDecoration(
                            labelText: 'Password',
                            prefixIcon: const Icon(Icons.lock_outline),
                            helperText: _register
                                ? 'Use at least 8 characters, up to 72 UTF-8 bytes.'
                                : null,
                            helperMaxLines: 2,
                            suffixIcon: IconButton(
                              tooltip: _visible
                                  ? 'Hide password'
                                  : 'Show password',
                              onPressed: () =>
                                  setState(() => _visible = !_visible),
                              icon: Icon(
                                _visible
                                    ? Icons.visibility_off_outlined
                                    : Icons.visibility_outlined,
                              ),
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Enter your password.';
                            }
                            if (_register && value.length < 8) {
                              return 'Use at least 8 characters.';
                            }
                            if (_register && utf8.encode(value).length > 72) {
                              return 'Use a password within 72 UTF-8 bytes.';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 24),
                        FilledButton(
                          key: const Key('auth-submit'),
                          onPressed: widget.auth.busy ? null : _submit,
                          child: widget.auth.busy
                              ? const SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : Text(_register ? 'Create account' : 'Sign in'),
                        ),
                        const SizedBox(height: 14),
                        TextButton(
                          onPressed: widget.auth.busy
                              ? null
                              : () {
                                  _form.currentState?.reset();
                                  setState(() {
                                    _register = !_register;
                                    _password.clear();
                                  });
                                },
                          child: Text(
                            _register
                                ? 'Already have an account? Sign in'
                                : 'New here? Create an account',
                          ),
                        ),
                        const SizedBox(height: 24),
                        const Text(
                          'Your wardrobe, thoughtfully put together.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFF52645B),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
          return Row(
            children: [
              if (wide)
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.all(20),
                    padding: const EdgeInsets.all(48),
                    decoration: BoxDecoration(
                      color: AppTheme.ink,
                      borderRadius: BorderRadius.circular(32),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'LESS GUESSWORK. MORE YOU.',
                          style: TextStyle(
                            color: Color(0xFFD5E1C6),
                            letterSpacing: 2,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const Spacer(),
                        const Center(
                          child: Icon(
                            Icons.checkroom_rounded,
                            size: 170,
                            color: Color(0xFFD5E1C6),
                          ),
                        ),
                        const SizedBox(height: 48),
                        const Text(
                          'A fresh perspective\non your everyday.',
                          style: TextStyle(
                            fontFamily: 'Georgia',
                            fontSize: 40,
                            color: Colors.white,
                            height: 1.15,
                          ),
                        ),
                        const SizedBox(height: 18),
                        const Text(
                          'Discover combinations you already own.\nDress for your day, and the weather.',
                          style: TextStyle(
                            color: Color(0xFFD5E1C6),
                            fontSize: 16,
                            height: 1.6,
                          ),
                        ),
                        const Spacer(),
                        const Text(
                          'YOUR PERSONAL WARDROBE COMPANION',
                          style: TextStyle(
                            color: Color(0xFFD5E1C6),
                            letterSpacing: 1.5,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              Expanded(child: form),
            ],
          );
        },
      ),
    ),
  );
}
