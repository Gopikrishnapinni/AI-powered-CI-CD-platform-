package com.example.ciplatform;

import java.time.Instant;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class GreetingController {
    private final String environment;

    public GreetingController(@Value("${APP_ENV:local}") String environment) {
        this.environment = environment;
    }

    @GetMapping("/greetings")
    public Map<String, String> greeting() {
        return Map.of(
                "message", "Deployment platform is healthy",
                "environment", environment,
                "timestamp", Instant.now().toString());
    }
}
