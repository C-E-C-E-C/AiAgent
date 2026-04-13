package com.example.saapp.service.impl;

import com.example.saapp.service.AuthCacheService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

@Service
public class AuthCacheServiceImpl implements AuthCacheService {
    private static final String PERM_KEY_PREFIX = "auth:perm:";
    private static final String ROLE_KEY_PREFIX = "auth:role:";
    private static final Duration CACHE_TTL = Duration.ofHours(1);

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    @Override
    public List<String> getCachedPerms(Long userId) {
        return readList(PERM_KEY_PREFIX + userId);
    }

    @Override
    public List<String> getCachedRoles(Long userId) {
        return readList(ROLE_KEY_PREFIX + userId);
    }

    @Override
    public void cachePerms(Long userId, List<String> perms) {
        writeList(PERM_KEY_PREFIX + userId, perms);
    }

    @Override
    public void cacheRoles(Long userId, List<String> roles) {
        writeList(ROLE_KEY_PREFIX + userId, roles);
    }

    @Override
    public void evictUser(Long userId) {
        stringRedisTemplate.delete(List.of(PERM_KEY_PREFIX + userId, ROLE_KEY_PREFIX + userId));
    }

    @Override
    public void evictUsers(Collection<Long> userIds) {
        if (userIds == null || userIds.isEmpty()) {
            return;
        }
        for (Long userId : userIds) {
            evictUser(userId);
        }
    }

    private List<String> readList(String key) {
        String value = stringRedisTemplate.opsForValue().get(key);
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return objectMapper.readValue(value, new TypeReference<List<String>>() {});
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("读取 Redis 缓存失败: " + key, e);
        }
    }

    private void writeList(String key, List<String> values) {
        try {
            List<String> safeValues = values == null ? Collections.emptyList() : new ArrayList<>(values);
            stringRedisTemplate.opsForValue().set(key, objectMapper.writeValueAsString(safeValues), CACHE_TTL);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("写入 Redis 缓存失败: " + key, e);
        }
    }
}