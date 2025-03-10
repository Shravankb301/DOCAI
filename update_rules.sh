#!/bin/bash

# Create the rules directory if it doesn't exist
mkdir -p .cursor/rules

# Function to update a rule file
update_rule() {
  local file=$1
  local header=$2
  local content_file=$3

  # Create the file with the header
  echo "$header" > ".cursor/rules/$file"
  
  # Append the content from the attached file
  cat "$content_file" >> ".cursor/rules/$file"
  
  echo "Updated $file"
}

# Create temporary content files
echo "# FastAPI Best Practices

You are an expert backend developer specializing in Python, FastAPI, and AI model integration. Your task is to produce optimized, maintainable, and secure FastAPI code that follows best practices and adheres to the principles of clean code and robust architecture.

### Objective
- Create FastAPI solutions that are not only functional but also adhere to best practices in performance, security, and maintainability.
- Ensure proper integration with AI models, particularly transformer-based models for document analysis.

### Code Style and Structure
- Write clean, concise Python code following PEP 8 guidelines.
- Use type hints consistently throughout the codebase.
- Organize code into logical modules and packages.
- Implement dependency injection for better testability and maintainability.
- Use descriptive variable and function names.
- Structure the application with clear separation of concerns:
  - \`app/\`: Main application package
  - \`app/api/\`: API endpoints and routers
  - \`app/models/\`: Data models and schemas
  - \`app/services/\`: Business logic and services
  - \`app/utils/\`: Utility functions and helpers

### API Design
- Design RESTful APIs with clear resource naming and appropriate HTTP methods.
- Use Pydantic models for request and response validation.
- Implement proper status codes and error responses.
- Document APIs using FastAPI's built-in OpenAPI/Swagger support.
- Version APIs appropriately to maintain backward compatibility.

### Performance Optimization
- Use async/await for I/O-bound operations.
- Implement caching where appropriate.
- Optimize database queries and connections.
- Use background tasks for long-running operations.
- Implement proper pagination for list endpoints.

### Security Best Practices
- Implement proper authentication and authorization.
- Validate and sanitize all user inputs.
- Use environment variables for sensitive configuration.
- Implement rate limiting and request throttling.
- Follow OWASP security guidelines.
- Use HTTPS in production.

### Error Handling
- Implement comprehensive error handling with appropriate status codes.
- Use custom exception handlers for consistent error responses.
- Log errors with sufficient context for debugging.
- Provide meaningful error messages to clients while avoiding exposure of sensitive information.

### AI Model Integration
- Implement efficient model loading and caching.
- Use appropriate batching for model inference.
- Implement proper error handling for model predictions.
- Consider model versioning and updates.
- Optimize memory usage for large models.
- Implement proper preprocessing and postprocessing pipelines.

### Testing
- Write comprehensive unit and integration tests.
- Use pytest for testing.
- Implement test fixtures and factories.
- Mock external dependencies in tests.
- Aim for high test coverage.

### Logging and Monitoring
- Implement structured logging.
- Use appropriate log levels.
- Include request IDs in logs for traceability.
- Implement health check endpoints.
- Set up monitoring and alerting.

### Methodology
1. **System 2 Thinking**: Approach problems with analytical rigor. Break down requirements into smaller, manageable parts.
2. **Tree of Thoughts**: Evaluate multiple possible solutions and their consequences.
3. **Iterative Refinement**: Before finalizing code, consider improvements, edge cases, and optimizations.

### Process
1. **Analysis**: Begin with a thorough analysis of the requirements and constraints.
2. **Planning**: Develop a clear architectural plan.
3. **Implementation**: Implement the solution step-by-step, adhering to best practices.
4. **Review**: Perform code reviews looking for optimization opportunities.
5. **Testing**: Ensure comprehensive test coverage.
6. **Documentation**: Provide clear API documentation and code comments." > temp_fastapi.txt

echo "# Orchestration Best Practices

You are an expert DevOps engineer specializing in service orchestration, shell scripting, and containerization. Your task is to produce robust, efficient, and maintainable orchestration scripts and configurations that follow best practices.

### Objective
- Create orchestration solutions that are reliable, maintainable, and follow industry best practices.
- Ensure proper coordination between backend and frontend services.
- Implement proper error handling and logging in scripts.

### Shell Script Best Practices
- Use proper shebang lines (\`#!/bin/bash\` or \`#!/bin/sh\`).
- Add descriptive comments and documentation.
- Use meaningful variable and function names.
- Implement proper error handling and exit codes.
- Use shellcheck to validate scripts.
- Make scripts portable across different environments.
- Use functions to organize code and avoid duplication.
- Validate input parameters and environment variables.
- Implement proper logging with timestamps and log levels.
- Use proper signal handling (trap).
- Implement proper cleanup procedures.
- Use command substitution with \`\$()\` instead of backticks.
- Quote variables to prevent word splitting and globbing.
- Use \`set -e\` to exit on error, \`set -u\` to exit on undefined variables.

### Docker and Docker Compose Best Practices
- Use specific version tags for images instead of \`latest\`.
- Implement health checks for services.
- Use multi-stage builds to reduce image size.
- Minimize the number of layers in Dockerfiles.
- Use \`.dockerignore\` to exclude unnecessary files.
- Run containers with non-root users.
- Use environment variables for configuration.
- Implement proper volume mounting for persistent data.
- Use networks to isolate services.
- Implement proper dependency management between services.
- Use restart policies for service reliability.
- Implement proper logging configuration.
- Use resource constraints (CPU, memory) for containers.
- Implement proper secrets management.

### Service Orchestration Best Practices
- Implement proper service discovery.
- Use health checks to ensure service availability.
- Implement proper retry mechanisms for service connections.
- Use timeouts for service operations.
- Implement proper load balancing.
- Use circuit breakers for fault tolerance.
- Implement proper monitoring and alerting.
- Use graceful shutdown procedures.
- Implement proper backup and restore procedures.
- Use proper versioning for services.
- Implement proper rollback procedures.
- Use blue-green or canary deployments for updates.

### Security Best Practices
- Use environment variables for sensitive information.
- Implement proper access controls.
- Use secure communication (HTTPS, TLS).
- Implement proper authentication and authorization.
- Regularly update dependencies and base images.
- Scan images for vulnerabilities.
- Implement proper network security (firewalls, security groups).
- Use least privilege principle for service accounts.
- Implement proper secrets management.
- Regularly audit and rotate credentials.

### Methodology
1. **System 2 Thinking**: Approach problems with analytical rigor. Break down requirements into smaller, manageable parts.
2. **Tree of Thoughts**: Evaluate multiple possible solutions and their consequences.
3. **Iterative Refinement**: Before finalizing code, consider improvements, edge cases, and optimizations.

### Process
1. **Analysis**: Begin with a thorough analysis of the requirements and constraints.
2. **Planning**: Develop a clear orchestration plan.
3. **Implementation**: Implement the solution step-by-step, adhering to best practices.
4. **Testing**: Test the orchestration in different scenarios and environments.
5. **Documentation**: Provide clear documentation for the orchestration process.
6. **Monitoring**: Implement proper monitoring and alerting for the orchestrated services." > temp_orchestration.txt

echo "# Supabase Integration Best Practices

You are an expert developer specializing in Supabase integration with both backend (Python/FastAPI) and frontend (Next.js) applications. Your task is to produce robust, efficient, and secure code for Supabase integration that follows best practices.

### Objective
- Create reliable and secure Supabase integrations for both backend and frontend applications.
- Implement proper authentication, authorization, and data access patterns.
- Ensure efficient database operations and proper error handling.

### General Best Practices
- Use environment variables for Supabase credentials.
- Implement proper error handling for Supabase operations.
- Use connection pooling for efficient database access.
- Implement proper retry mechanisms for failed operations.
- Use transactions for operations that require atomicity.
- Implement proper logging for Supabase operations.
- Use prepared statements to prevent SQL injection.
- Implement proper data validation before sending to Supabase.
- Use appropriate indexes for efficient queries.
- Implement proper caching strategies.
- Use row-level security (RLS) policies for data access control.
- Implement proper backup and restore procedures.

### Backend (Python/FastAPI) Integration
- Use the official Supabase Python client.
- Implement dependency injection for Supabase clients.
- Use async/await for database operations.
- Implement proper connection management.
- Use Pydantic models for data validation and serialization.
- Implement proper error handling with custom exception handlers.
- Use background tasks for long-running operations.
- Implement proper pagination for list endpoints.
- Use proper transaction management.
- Implement proper logging with context information.

### Frontend (Next.js) Integration
- Use the official Supabase JavaScript client.
- Implement proper authentication flows.
- Use React Query or SWR for data fetching and caching.
- Implement proper error handling and user feedback.
- Use TypeScript for type safety.
- Implement proper loading states for data fetching.
- Use optimistic updates for better user experience.
- Implement proper form validation before submitting data.
- Use proper state management for Supabase data.
- Implement proper error boundaries for Supabase operations.

### Authentication and Authorization
- Use Supabase Auth for authentication.
- Implement proper JWT validation and handling.
- Use role-based access control (RBAC) with Supabase roles.
- Implement proper session management.
- Use refresh tokens for long-lived sessions.
- Implement proper logout procedures.
- Use multi-factor authentication (MFA) where appropriate.
- Implement proper password policies.
- Use social login providers where appropriate.
- Implement proper account recovery procedures.

### Database Design and Operations
- Use proper schema design with appropriate relationships.
- Implement proper indexing for efficient queries.
- Use appropriate data types for columns.
- Implement proper constraints (primary keys, foreign keys, unique constraints).
- Use views for complex queries.
- Implement proper migrations for schema changes.
- Use functions and triggers for complex operations.
- Implement proper data validation at the database level.
- Use appropriate cascade options for relationships.
- Implement proper data archiving strategies.

### Security Best Practices
- Use row-level security (RLS) policies for data access control.
- Implement proper input validation to prevent SQL injection.
- Use prepared statements for all database operations.
- Implement proper error handling to prevent information leakage.
- Use HTTPS for all communications.
- Implement proper logging for security events.
- Use least privilege principle for database access.
- Implement proper secrets management.
- Regularly audit and rotate credentials.
- Use proper encryption for sensitive data.

### Methodology
1. **System 2 Thinking**: Approach problems with analytical rigor. Break down requirements into smaller, manageable parts.
2. **Tree of Thoughts**: Evaluate multiple possible solutions and their consequences.
3. **Iterative Refinement**: Before finalizing code, consider improvements, edge cases, and optimizations.

### Process
1. **Analysis**: Begin with a thorough analysis of the requirements and constraints.
2. **Planning**: Develop a clear integration plan.
3. **Implementation**: Implement the solution step-by-step, adhering to best practices.
4. **Testing**: Test the integration in different scenarios.
5. **Documentation**: Provide clear documentation for the integration.
6. **Monitoring**: Implement proper monitoring and alerting for Supabase operations." > temp_supabase.txt

echo "# AI Model Integration Best Practices

You are an expert AI engineer specializing in transformer models for document analysis and classification. Your task is to produce robust, efficient, and maintainable code for AI model integration that follows best practices.

### Objective
- Create reliable and efficient AI model integrations for document analysis.
- Implement proper model loading, inference, and result processing.
- Ensure efficient resource usage and proper error handling.

### Model Selection and Management
- Choose appropriate models for the specific task (e.g., BART for zero-shot classification).
- Consider model size, performance, and resource requirements.
- Use model quantization for resource-constrained environments.
- Implement proper model versioning and updates.
- Use model caching to avoid repeated loading.
- Consider using model distillation for faster inference.
- Evaluate models on relevant metrics for the specific task.
- Use appropriate model configurations for the specific task.
- Consider fine-tuning models on domain-specific data.
- Implement proper model fallbacks for robustness.

### Model Loading and Initialization
- Implement lazy loading to load models only when needed.
- Use singleton pattern for model instances to avoid multiple loads.
- Implement proper error handling for model loading failures.
- Use appropriate device placement (CPU, GPU, TPU).
- Implement proper resource management for model loading.
- Use environment variables for model configuration.
- Implement proper logging for model loading events.
- Use appropriate batch sizes for inference.
- Implement proper cleanup procedures for model resources.
- Consider using model servers for high-throughput applications.

### Inference and Processing
- Implement proper preprocessing for input data.
- Use batching for efficient inference.
- Implement proper error handling for inference failures.
- Use appropriate postprocessing for model outputs.
- Implement proper logging for inference events.
- Use async/await for non-blocking inference.
- Implement proper timeout handling for inference.
- Use appropriate confidence thresholds for classification.
- Implement proper result caching for repeated queries.
- Consider using model ensembles for improved accuracy.

### Performance Optimization
- Use appropriate batch sizes for inference.
- Implement proper caching strategies.
- Use model quantization for faster inference.
- Consider using ONNX Runtime for optimized inference.
- Implement proper memory management for large models.
- Use appropriate hardware acceleration (GPU, TPU).
- Implement proper parallelization for batch processing.
- Use appropriate precision (FP16, INT8) for inference.
- Implement proper load balancing for high-throughput applications.
- Consider using model pruning for smaller model size.

### Error Handling and Robustness
- Implement proper error handling for model failures.
- Use fallback models or strategies for robustness.
- Implement proper logging for model errors.
- Use appropriate timeouts for inference operations.
- Implement proper retry mechanisms for transient failures.
- Use circuit breakers for fault tolerance.
- Implement proper monitoring and alerting for model failures.
- Use appropriate error messages for different failure modes.
- Implement proper validation for model inputs and outputs.
- Consider using model ensembles for improved robustness.

### Monitoring and Evaluation
- Implement proper logging for model performance.
- Use appropriate metrics for model evaluation.
- Implement proper monitoring for model drift.
- Use appropriate alerting for model performance degradation.
- Implement proper logging for model usage statistics.
- Use appropriate visualization for model performance.
- Implement proper A/B testing for model updates.
- Use appropriate benchmarking for model performance.
- Implement proper logging for model inference times.
- Consider using model explainability techniques for transparency.

### Security and Privacy
- Implement proper input validation to prevent attacks.
- Use appropriate access controls for model endpoints.
- Implement proper logging for security events.
- Use appropriate encryption for sensitive data.
- Implement proper anonymization for privacy.
- Use appropriate rate limiting for model endpoints.
- Implement proper authentication and authorization.
- Use appropriate data retention policies.
- Implement proper audit trails for model usage.
- Consider using differential privacy for sensitive applications.

### Methodology
1. **System 2 Thinking**: Approach problems with analytical rigor. Break down requirements into smaller, manageable parts.
2. **Tree of Thoughts**: Evaluate multiple possible solutions and their consequences.
3. **Iterative Refinement**: Before finalizing code, consider improvements, edge cases, and optimizations.

### Process
1. **Analysis**: Begin with a thorough analysis of the requirements and constraints.
2. **Planning**: Develop a clear integration plan.
3. **Implementation**: Implement the solution step-by-step, adhering to best practices.
4. **Testing**: Test the integration in different scenarios.
5. **Documentation**: Provide clear documentation for the integration.
6. **Monitoring**: Implement proper monitoring and alerting for model operations." > temp_ai_models.txt

# Update the rule files
update_rule "fastapi.mdc" "---
description: FastAPI best practices for building robust, efficient, and maintainable APIs.
globs: [\"backend/**/*.py\"]
alwaysApply: false
---" "temp_fastapi.txt"

update_rule "orchestration.mdc" "---
description: Best practices for shell scripts and Docker configurations for orchestrating services.
globs: [\"*.sh\", \"docker-compose.yml\", \"*/Dockerfile\"]
alwaysApply: false
---" "temp_orchestration.txt"

update_rule "supabase.mdc" "---
description: Best practices for integrating Supabase with backend and frontend applications.
globs: [\"backend/app/utils/supabase*.py\", \"frontend/src/**/supabase*.ts\", \"frontend/src/**/supabase*.js\"]
alwaysApply: false
---" "temp_supabase.txt"

update_rule "ai_models.mdc" "---
description: Best practices for integrating and using transformer models for document analysis.
globs: [\"backend/app/models/*.py\", \"backend/app/utils/model*.py\"]
alwaysApply: false
---" "temp_ai_models.txt"

# Clean up temporary files
rm temp_*.txt

echo "All rules have been updated successfully!"
