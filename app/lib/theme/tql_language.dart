import 'package:highlight/highlight.dart';

/// Custom language definition for Thompson Query Language (TQL).
final tql = Mode(
  refs: {},
  aliases: ['tql'],
  keywords: {
    'keyword': 'where and or locations',
    'operator': 'contains contains-any == !=',
  },
  contains: [
    Mode(
      className: 'string',
      begin: '"',
      end: '"',
      relevance: 0,
    ),
    Mode(
      className: 'type', // Field names
      begin: r't_\w+',
      relevance: 10,
    ),
    Mode(
      className: 'number',
      begin: r'\[.*?\]',
      relevance: 0,
    ),
  ],
);
