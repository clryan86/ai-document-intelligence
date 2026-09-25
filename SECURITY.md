# Security Policy

This repository is a portfolio application, not a hosted production document-processing service.

## Reporting

Please report suspected vulnerabilities privately to the repository owner rather than opening a public issue.

## Current controls

The application restricts document extensions, caps upload size, removes directory components from uploaded filenames, prevents duplicate ingestion by SHA-256, and never fetches user-supplied remote URLs.

## Production hardening

A public deployment should add authentication/authorization, rate limiting, malware scanning, encrypted object storage, secure headers, observability, dependency scanning, backup policies, and a formal data-retention policy.
