package com.example.saapp.service;

import java.util.Collection;
import java.util.List;

public interface AuthCacheService {
    List<String> getCachedPerms(Long userId);

    List<String> getCachedRoles(Long userId);

    void cachePerms(Long userId, List<String> perms);

    void cacheRoles(Long userId, List<String> roles);

    void evictUser(Long userId);

    void evictUsers(Collection<Long> userIds);
}