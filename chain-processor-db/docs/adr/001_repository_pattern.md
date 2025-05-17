# ADR-001: Repository Pattern for Data Access

## Status
Accepted

## Context
In designing the database layer for the Chain Processing System, we needed to establish a clear pattern for data access that would support:

1. Separation of concerns between data access and business logic
2. Testability through mocking of database interactions
3. Type safety and IDE autocomplete support
4. Consistent error handling and transaction management
5. Adherence to SOLID principles, particularly the Dependency Inversion Principle

The application will be handling complex domain models with various relationships between them, and we wanted a clean approach that would reduce duplication of data access code while providing a well-defined interface for other components.

## Decision
We have decided to adopt the Repository Pattern for data access in the Chain Processing System. Specifically:

1. Each domain entity will have a corresponding repository class (e.g., `UserRepository`, `NodeRepository`)
2. All repositories will inherit from a generic `BaseRepository[T]` class that provides common CRUD operations
3. Repositories will accept a SQLAlchemy `Session` object during initialization, allowing for dependency injection
4. Domain-specific query methods will be implemented in the specialized repository classes
5. Each repository will handle transactions at its boundaries, committing changes when appropriate

To enhance the type safety and developer experience, we are using Python's generic typing with SQLAlchemy models:

```python
T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: Session):
        self.db = db
        self.model_class = cast(Type[T], get_args(self.__class__.__orig_bases__[0])[0])
```

This approach allows us to create strongly-typed repositories where methods return the correct model types.

## Consequences

### Positive
- Clear separation between database access and business logic
- Consistent interface for data operations across the system
- Improved testability through dependency injection
- Type safety benefits through Python's generics
- Reduced duplication of CRUD operation code
- Easy to add specialized query methods for specific domain entities

### Negative
- Additional layer of abstraction which adds some complexity
- Some boilerplate code required for each repository
- Must ensure transactions are managed correctly at repository boundaries

## Alternatives Considered

### Direct Use of SQLAlchemy ORM
We considered directly using SQLAlchemy's ORM in service layers without a repository abstraction. While this would have reduced the number of layers, it would have made testing more difficult and could lead to scattered data access logic throughout the codebase.

### Active Record Pattern
The Active Record pattern, where models contain their own data access methods, was considered but rejected as it would violate the single responsibility principle and make testing more complex.

### Data Access Objects (DAOs)
DAOs are similar to repositories but typically tied more closely to specific data stores. We preferred repositories as they abstract the underlying storage mechanism more completely.

## References
- SQLAlchemy ORM documentation: https://docs.sqlalchemy.org/en/20/orm/
- Repository Pattern: https://martinfowler.com/eaaCatalog/repository.html
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID 