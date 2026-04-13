package com.example.saapp.controller;

import cn.dev33.satoken.stp.StpUtil;
import cn.dev33.satoken.secure.BCrypt;
import cn.dev33.satoken.util.SaResult;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.example.saapp.mapper.SysUserMapper;
import com.example.saapp.vo.SysUser;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/api")
public class LoginController {

    @Autowired
    private SysUserMapper sysUserMapper;

    @PostMapping("/login")
    public SaResult login(@RequestParam  String username, @RequestParam   String password) {

        log.info("username: {}, password: {}", username, password);
        // 查我们自己的表：sys_user
        SysUser user = sysUserMapper.selectOne(
                Wrappers.lambdaQuery(SysUser.class)
                        .eq(SysUser::getUsername, username)
        );

        if (user == null) {
            log.error("用户不存在: {}", username);
            return SaResult.error("用户不存在");
        }

        // 密码校验
        if (!BCrypt.checkpw(password, user.getPassword())) {
            log.error("密码错误: {}", username);
            return SaResult.error("密码错误");
        }

        // 存储用户角色
        String roleCode = sysUserMapper.selectRoleCodeByUserId(user.getId());
        log.info("roleCode: {}", roleCode);
        // Sa-Token 登录
        StpUtil.login(user.getId());

        log.info("登录成功: {}", username);
        String token = StpUtil.getTokenValue();
        return SaResult.ok("登录成功").set("role",roleCode).set("username",user.getUsername()).set("token",token).
                set("perms",StpUtil.getPermissionList(user.getId()));
    }

    @PostMapping("/logout")
    public SaResult logout() {
        StpUtil.logout();
        log.info("退出成功");
        return SaResult.ok("退出成功");
    }

    @GetMapping("/islogin")
    public SaResult isLogin() {
        return SaResult.ok("已登录").set("isLogin", StpUtil.isLogin());
    }
}