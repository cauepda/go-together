# Go Together - Amazon Q Developer Rules

## Project Context
This is a ride-sharing matching system built with FastAPI and MCP AWS Pricing integration.

## Code Style
- Use Python 3.8+ features
- Follow PEP 8 conventions
- Prefer type hints
- Use FastAPI for REST APIs
- Use Streamlit for web interfaces

## Architecture Patterns
- Keep business logic in separate modules
- Use dependency injection for services
- Implement proper error handling
- Follow REST API conventions

## AWS Integration
- Use boto3 for AWS services
- Implement proper credential management
- Follow AWS best practices for Lambda
- Use CDK for infrastructure as code

## MCP Integration
- Follow MCP protocol specifications
- Use stdio for communication
- Implement proper error handling
- Support natural language prompts

## Testing
- Write unit tests for core functions
- Include integration tests for MCP
- Test API endpoints thoroughly
- Use pytest framework