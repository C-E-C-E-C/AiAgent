package com.example.saapp.service.impl;

import cn.dev33.satoken.secure.BCrypt;
import cn.dev33.satoken.stp.StpUtil;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysUserMapper;
import com.example.saapp.service.AuthCacheService;
import com.example.saapp.service.SysUserService;
import com.example.saapp.vo.SysUser;
import com.example.saapp.mapper.SysUserRoleMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.List;

@Service
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements SysUserService {
    @Autowired
    private SysUserRoleMapper sysUserRoleMapper;

    @Autowired
    private AuthCacheService authCacheService;

    @Override
    public List<SysUser> listWithRelation() {
        return baseMapper.selectUserListWithRelation();
    }

    @Override
    public SysUser getWithRelation(Long id) {
        return baseMapper.selectUserByIdWithRelation(id);
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public boolean saveOrUpdateEncrypt(SysUser user) {
        if (user.getPassword() != null && !user.getPassword().isBlank()) {
            String encoded = BCrypt.hashpw(user.getPassword(), BCrypt.gensalt());
            user.setPassword(encoded);
        }
        boolean saved = saveOrUpdate(user);
        syncUserRole(user.getId(), user.getRoleId());
        invalidateUserAfterCommit(user.getId());
        return saved;
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public boolean removeWithRelation(Long id) {
        sysUserRoleMapper.deleteByUserId(id);
        boolean removed = removeById(id);
        invalidateUserAfterCommit(id);
        return removed;
    }

    private void syncUserRole(Long userId, Long roleId) {
        sysUserRoleMapper.deleteByUserId(userId);
        if (roleId != null) {
            sysUserRoleMapper.insertUserRole(userId, roleId);
        }
    }

    private void invalidateUserAfterCommit(Long userId) {
        if (userId == null) {
            return;
        }

        Runnable action = () -> {
            authCacheService.evictUser(userId);
            StpUtil.kickout(userId);
        };

        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    action.run();
                }
            });
            return;
        }

        action.run();
    }


}
