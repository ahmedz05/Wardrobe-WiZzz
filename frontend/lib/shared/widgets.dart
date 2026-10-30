import 'package:flutter/material.dart';

import '../core/app_theme.dart';

class Brand extends StatelessWidget {
  const Brand({super.key, this.light = false});
  final bool light;
  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Icon(
        Icons.checkroom_rounded,
        size: 28,
        color: light ? Colors.white : AppTheme.ink,
      ),
      const SizedBox(width: 10),
      Flexible(
        child: Text(
          'Wardrobe-WIZzz',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 18,
            letterSpacing: -.5,
            color: light ? Colors.white : AppTheme.ink,
          ),
        ),
      ),
    ],
  );
}

class MessageBox extends StatelessWidget {
  const MessageBox(this.message, {super.key, this.isError = true});
  final String message;
  final bool isError;
  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isError
            ? Theme.of(context).colorScheme.errorContainer
            : AppTheme.sage,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(
        message,
        style: TextStyle(
          color: isError
              ? Theme.of(context).colorScheme.onErrorContainer
              : AppTheme.ink,
        ),
      ),
    ),
  );
}

class StatePanel extends StatelessWidget {
  const StatePanel({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.action,
    this.actionLabel,
  });
  final IconData icon;
  final String title, message;
  final VoidCallback? action;
  final String? actionLabel;
  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 36,
              backgroundColor: AppTheme.sage,
              child: Icon(icon, size: 32, color: AppTheme.ink),
            ),
            const SizedBox(height: 20),
            Text(
              title,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 10),
            Text(message, textAlign: TextAlign.center),
            if (action != null) ...[
              const SizedBox(height: 22),
              FilledButton(
                onPressed: action,
                child: Text(actionLabel ?? 'Try again'),
              ),
            ],
          ],
        ),
      ),
    ),
  );
}

class SectionHeading extends StatelessWidget {
  const SectionHeading({
    super.key,
    required this.eyebrow,
    required this.title,
    required this.subtitle,
  });
  final String eyebrow, title, subtitle;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        eyebrow.toUpperCase(),
        style: const TextStyle(
          color: AppTheme.rust,
          fontWeight: FontWeight.w700,
          letterSpacing: 2,
          fontSize: 11,
        ),
      ),
      const SizedBox(height: 10),
      Text(title, style: Theme.of(context).textTheme.headlineLarge),
      const SizedBox(height: 8),
      Text(
        subtitle,
        style: Theme.of(
          context,
        ).textTheme.bodyLarge?.copyWith(color: const Color(0xFF52645B)),
      ),
    ],
  );
}
