package com.example.saapp;


import cn.dev33.satoken.SaManager;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication

public class SaAppApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaAppApplication.class, args);
        System.out.print("启动成功,sa-token配置如下"+ SaManager.getConfig());
    }
}
