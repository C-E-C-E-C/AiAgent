package com.example.saapp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * 密码加密器配置
 */
@Configuration
public class PasswordConfig {

    /**
     * 注册 BCrypt 密码加密器为 Bean
     * 这样 Controller 就能 @Autowired 注入了
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}