package com.example.ciplatform;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(GreetingController.class)
class GreetingControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void returnsDeploymentHealthMessage() throws Exception {
        mockMvc.perform(get("/api/v1/greetings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Deployment platform is healthy"));
    }
}
