package com.elca.ch.counter.controller;

import com.elca.ch.counter.response.CounterResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CounterController {

    private int i = 0;

    @CrossOrigin()
    @GetMapping("/")
    public ResponseEntity<CounterResponse> index() {
        CounterResponse response = new CounterResponse(i++);
        return ResponseEntity.ok().body(response);
    }

}