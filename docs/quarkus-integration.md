# Quarkus Microservices Configuration Templates

## Application Properties (src/main/resources/application.properties)

```properties
# Keycloak OIDC Configuration
quarkus.oidc.auth-server-url=https://iam.padmini.systems/realms/padmini-systems
quarkus.oidc.client-id=asm-microservices
quarkus.oidc.credentials.secret=asm-microservices-secret-change-me
quarkus.oidc.application-type=service
quarkus.oidc.token.verify-access-token-with-user-info=true

# Token validation
quarkus.oidc.token.issuer=https://iam.padmini.systems/realms/padmini-systems
quarkus.oidc.token.audience=asm-microservices

# Security roles mapping
quarkus.security.jaxrs.deny-unannotated-endpoints=true

# CORS Configuration
quarkus.http.cors=true
quarkus.http.cors.origins=https://ppcs.padmini.systems,https://app.padmini.systems,http://localhost:3000
quarkus.http.cors.headers=accept,authorization,content-type,x-requested-with
quarkus.http.cors.methods=GET,POST,PUT,DELETE,OPTIONS

# Database Configuration (adjust as needed)
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=padmini_user
quarkus.datasource.password=your-db-password
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/padmini_db

# Hibernate ORM
quarkus.hibernate-orm.database.generation=update
quarkus.hibernate-orm.log.sql=true

# Logging
quarkus.log.level=INFO
quarkus.log.category."io.quarkus.oidc".level=DEBUG
```

## User Profile Entity (src/main/java/systems/padmini/entity/UserProfile.java)

```java
package systems.padmini.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "user_profiles")
public class UserProfile extends PanacheEntityBase {

    @Id
    public UUID id;

    @Column(name = "keycloak_id", unique = true, nullable = false)
    public String keycloakId;

    @Column(name = "username", unique = true, nullable = false)
    public String username;

    @Column(name = "email", unique = true, nullable = false)
    public String email;

    @Column(name = "mobile", nullable = false)
    public String mobile;

    @Column(name = "first_name")
    public String firstName;

    @Column(name = "last_name")
    public String lastName;

    @Column(name = "full_name")
    public String fullName;

    @Column(name = "business_type")
    public String businessType;

    @Column(name = "company_name")
    public String companyName;

    @Column(name = "address", columnDefinition = "TEXT")
    public String address;

    @Column(name = "additional_info", columnDefinition = "TEXT")
    public String additionalInfo;

    @Column(name = "is_onboarded")
    public Boolean isOnboarded = false;

    @Column(name = "created_at")
    public LocalDateTime createdAt;

    @Column(name = "updated_at")
    public LocalDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void preUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Static methods for queries
    public static UserProfile findByKeycloakId(String keycloakId) {
        return find("keycloakId", keycloakId).firstResult();
    }

    public static UserProfile findByUsername(String username) {
        return find("username", username).firstResult();
    }

    public static UserProfile findByEmail(String email) {
        return find("email", email).firstResult();
    }
}
```

## User Profile DTO (src/main/java/systems/padmini/dto/UserProfileDto.java)

```java
package systems.padmini.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public class UserProfileDto {
    public UUID id;
    public String keycloakId;
    public String username;
    public String email;
    public String mobile;
    public String firstName;
    public String lastName;
    public String fullName;
    public String businessType;
    public String companyName;
    public String address;
    public String additionalInfo;
    public Boolean isOnboarded;
    public LocalDateTime createdAt;
    public LocalDateTime updatedAt;

    // Constructors
    public UserProfileDto() {}

    public UserProfileDto(systems.padmini.entity.UserProfile entity) {
        this.id = entity.id;
        this.keycloakId = entity.keycloakId;
        this.username = entity.username;
        this.email = entity.email;
        this.mobile = entity.mobile;
        this.firstName = entity.firstName;
        this.lastName = entity.lastName;
        this.fullName = entity.fullName;
        this.businessType = entity.businessType;
        this.companyName = entity.companyName;
        this.address = entity.address;
        this.additionalInfo = entity.additionalInfo;
        this.isOnboarded = entity.isOnboarded;
        this.createdAt = entity.createdAt;
        this.updatedAt = entity.updatedAt;
    }
}
```

## Onboarding Request DTO (src/main/java/systems/padmini/dto/OnboardingRequest.java)

```java
package systems.padmini.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public class OnboardingRequest {
    
    public static class UserProfile {
        @NotBlank(message = "User ID is required")
        public String userId;
        
        @NotBlank(message = "Username is required")
        public String username;
        
        @Email(message = "Valid email is required")
        public String email;
        
        @Pattern(regexp = "^[+]?[1-9]\\d{9,14}$", message = "Valid mobile number is required")
        public String mobile;
        
        public String name;
        public String firstName;
        public String lastName;
    }
    
    public static class AdditionalData {
        @NotBlank(message = "Business type is required")
        public String businessType;
        
        @NotBlank(message = "Company name is required")
        public String companyName;
        
        @NotBlank(message = "Address is required")
        public String address;
        
        public String additionalInfo;
    }
    
    public UserProfile userProfile;
    public AdditionalData additionalData;
    public String timestamp;
}
```

## User Service (src/main/java/systems/padmini/service/UserService.java)

```java
package systems.padmini.service;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import org.eclipse.microprofile.jwt.JsonWebToken;
import systems.padmini.dto.OnboardingRequest;
import systems.padmini.dto.UserProfileDto;
import systems.padmini.entity.UserProfile;

@ApplicationScoped
public class UserService {

    @Inject
    JsonWebToken jwt;

    @Transactional
    public UserProfileDto completeOnboarding(OnboardingRequest request) {
        // Get or create user profile
        UserProfile userProfile = UserProfile.findByKeycloakId(request.userProfile.userId);
        
        if (userProfile == null) {
            userProfile = new UserProfile();
            userProfile.keycloakId = request.userProfile.userId;
        }
        
        // Update profile with Keycloak data
        userProfile.username = request.userProfile.username;
        userProfile.email = request.userProfile.email;
        userProfile.mobile = request.userProfile.mobile;
        userProfile.firstName = request.userProfile.firstName;
        userProfile.lastName = request.userProfile.lastName;
        userProfile.fullName = request.userProfile.name;
        
        // Update with additional onboarding data
        userProfile.businessType = request.additionalData.businessType;
        userProfile.companyName = request.additionalData.companyName;
        userProfile.address = request.additionalData.address;
        userProfile.additionalInfo = request.additionalData.additionalInfo;
        userProfile.isOnboarded = true;
        
        userProfile.persistAndFlush();
        
        return new UserProfileDto(userProfile);
    }

    public UserProfileDto getCurrentUserProfile() {
        String keycloakId = jwt.getSubject();
        UserProfile userProfile = UserProfile.findByKeycloakId(keycloakId);
        
        if (userProfile == null) {
            throw new RuntimeException("User profile not found");
        }
        
        return new UserProfileDto(userProfile);
    }

    @Transactional
    public UserProfileDto updateUserProfile(UserProfileDto dto) {
        String keycloakId = jwt.getSubject();
        UserProfile userProfile = UserProfile.findByKeycloakId(keycloakId);
        
        if (userProfile == null) {
            throw new RuntimeException("User profile not found");
        }
        
        // Update allowed fields
        userProfile.businessType = dto.businessType;
        userProfile.companyName = dto.companyName;
        userProfile.address = dto.address;
        userProfile.additionalInfo = dto.additionalInfo;
        
        userProfile.persistAndFlush();
        
        return new UserProfileDto(userProfile);
    }

    public UserProfileDto getUserProfileFromToken() {
        // Extract user information from JWT token
        UserProfileDto dto = new UserProfileDto();
        dto.keycloakId = jwt.getSubject();
        dto.username = jwt.getClaim("preferred_username");
        dto.email = jwt.getClaim("email");
        dto.mobile = jwt.getClaim("mobile");
        dto.fullName = jwt.getClaim("name");
        dto.firstName = jwt.getClaim("given_name");
        dto.lastName = jwt.getClaim("family_name");
        
        return dto;
    }
}
```

## User Resource (src/main/java/systems/padmini/resource/UserResource.java)

```java
package systems.padmini.resource;

import jakarta.annotation.security.RolesAllowed;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.jwt.JsonWebToken;
import systems.padmini.dto.OnboardingRequest;
import systems.padmini.dto.UserProfileDto;
import systems.padmini.service.UserService;

@Path("/api/user")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RolesAllowed("user")
public class UserResource {

    @Inject
    UserService userService;

    @Inject
    JsonWebToken jwt;

    @POST
    @Path("/onboard")
    public Response completeOnboarding(@Valid OnboardingRequest request) {
        try {
            UserProfileDto profile = userService.completeOnboarding(request);
            return Response.ok(profile).build();
        } catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(new ErrorResponse("Onboarding failed: " + e.getMessage()))
                    .build();
        }
    }

    @GET
    @Path("/profile")
    public Response getUserProfile() {
        try {
            UserProfileDto profile = userService.getCurrentUserProfile();
            return Response.ok(profile).build();
        } catch (Exception e) {
            return Response.status(Response.Status.NOT_FOUND)
                    .entity(new ErrorResponse("Profile not found: " + e.getMessage()))
                    .build();
        }
    }

    @PUT
    @Path("/profile")
    public Response updateUserProfile(@Valid UserProfileDto profileDto) {
        try {
            UserProfileDto updated = userService.updateUserProfile(profileDto);
            return Response.ok(updated).build();
        } catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(new ErrorResponse("Update failed: " + e.getMessage()))
                    .build();
        }
    }

    @GET
    @Path("/token-info")
    public Response getTokenInfo() {
        try {
            UserProfileDto tokenInfo = userService.getUserProfileFromToken();
            return Response.ok(tokenInfo).build();
        } catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(new ErrorResponse("Token parsing failed: " + e.getMessage()))
                    .build();
        }
    }

    @GET
    @Path("/health")
    @RolesAllowed({"user", "admin"})
    public Response health() {
        return Response.ok(new HealthResponse("User service is healthy", jwt.getSubject())).build();
    }

    // Inner classes for responses
    public static class ErrorResponse {
        public String error;
        public ErrorResponse(String error) { this.error = error; }
    }

    public static class HealthResponse {
        public String status;
        public String userId;
        public HealthResponse(String status, String userId) {
            this.status = status;
            this.userId = userId;
        }
    }
}
```

## Security Configuration (src/main/java/systems/padmini/config/SecurityConfig.java)

```java
package systems.padmini.config;

import io.quarkus.oidc.OidcRequestContext;
import io.quarkus.oidc.OidcTenantConfig;
import io.quarkus.oidc.TenantConfigResolver;
import io.vertx.ext.web.RoutingContext;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class SecurityConfig implements TenantConfigResolver {

    @Override
    public OidcTenantConfig resolve(RoutingContext context, OidcRequestContext<OidcTenantConfig> requestContext) {
        // You can implement custom tenant resolution logic here if needed
        // For now, return null to use the default configuration
        return null;
    }
}
```

## Exception Mappers (src/main/java/systems/padmini/exception/GlobalExceptionMapper.java)

```java
package systems.padmini.exception;

import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import org.jboss.logging.Logger;

@Provider
public class GlobalExceptionMapper implements ExceptionMapper<Exception> {

    private static final Logger LOG = Logger.getLogger(GlobalExceptionMapper.class);

    @Override
    public Response toResponse(Exception exception) {
        LOG.error("Unhandled exception", exception);
        
        ErrorResponse error = new ErrorResponse(
            "Internal server error",
            500,
            exception.getMessage()
        );
        
        return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                .entity(error)
                .build();
    }

    public static class ErrorResponse {
        public String message;
        public int code;
        public String detail;
        
        public ErrorResponse(String message, int code, String detail) {
            this.message = message;
            this.code = code;
            this.detail = detail;
        }
    }
}
```

## Maven Dependencies (pom.xml additions)

```xml
<dependencies>
    <!-- Quarkus OIDC -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-oidc</artifactId>
    </dependency>
    
    <!-- Quarkus Security -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-security</artifactId>
    </dependency>
    
    <!-- Quarkus RESTEasy -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-resteasy-reactive-jackson</artifactId>
    </dependency>
    
    <!-- Quarkus Hibernate ORM with Panache -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-hibernate-orm-panache</artifactId>
    </dependency>
    
    <!-- PostgreSQL Driver -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-jdbc-postgresql</artifactId>
    </dependency>
    
    <!-- Validation -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-hibernate-validator</artifactId>
    </dependency>
    
    <!-- SmallRye JWT -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-smallrye-jwt</artifactId>
    </dependency>
</dependencies>
```

## Testing (src/test/java/systems/padmini/UserResourceTest.java)

```java
package systems.padmini;

import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.security.TestSecurity;
import io.quarkus.test.security.jwt.Claim;
import io.quarkus.test.security.jwt.JwtSecurity;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;

@QuarkusTest
public class UserResourceTest {

    @Test
    @TestSecurity(user = "testuser", roles = "user")
    @JwtSecurity(claims = {
        @Claim(key = "sub", value = "test-user-id"),
        @Claim(key = "preferred_username", value = "testuser"),
        @Claim(key = "email", value = "test@example.com"),
        @Claim(key = "mobile", value = "+919876543210")
    })
    public void testGetTokenInfo() {
        given()
            .when().get("/api/user/token-info")
            .then()
                .statusCode(200)
                .contentType(ContentType.JSON)
                .body("username", is("testuser"))
                .body("email", is("test@example.com"));
    }

    @Test
    @TestSecurity(user = "testuser", roles = "user")
    public void testHealthEndpoint() {
        given()
            .when().get("/api/user/health")
            .then()
                .statusCode(200)
                .contentType(ContentType.JSON)
                .body("status", is("User service is healthy"));
    }
}
```

## Usage Example

### 1. Start the application:
```bash
./mvnw quarkus:dev
```

### 2. Test token validation:
```bash
# Get token from Keycloak
TOKEN=$(curl -s -X POST "https://iam.padmini.systems/realms/padmini-systems/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=asm-microservices" \
  -d "client_secret=your-client-secret" \
  -d "grant_type=client_credentials" | jq -r '.access_token')

# Test API endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/user/health
```
