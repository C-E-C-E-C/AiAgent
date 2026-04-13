package com.example.saapp.config;

import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Knife4jConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Sa Demo API")
                .description("Backend starter with MySQL, Knife4j and Sa-Token")
                .version("1.0.0")
                .contact(new Contact().name("Copilot")))
            .externalDocs(new ExternalDocumentation().description("API Docs"));
    }
}
