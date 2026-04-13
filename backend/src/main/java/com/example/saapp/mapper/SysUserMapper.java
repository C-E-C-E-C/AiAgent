package com.example.saapp.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.saapp.vo.SysUser;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
    SysUser selectByUsername(String username);

    @Select("""
    SELECT r.role_key
    FROM sys_user_role ur
    JOIN sys_role r ON ur.role_id = r.id
    WHERE ur.user_id = #{userId}
    LIMIT 1;
""")
    String selectRoleCodeByUserId(Long userId);

    @Select("""
    SELECT r.role_key
    FROM sys_user_role ur
    JOIN sys_role r ON ur.role_id = r.id
    WHERE ur.user_id = #{userId}
""")
    List<String> selectRoleCodesByUserId(Long userId);

        @Select("""
        SELECT
            u.id,
            u.username,
            u.password,
            u.nick_name,
            u.dept_id,
            u.status,
            u.create_time,
            u.update_time,
            d.dept_name AS dept_name,
            (SELECT ur.role_id FROM sys_user_role ur WHERE ur.user_id = u.id LIMIT 1) AS role_id,
            (SELECT r.role_key FROM sys_user_role ur JOIN sys_role r ON ur.role_id = r.id WHERE ur.user_id = u.id LIMIT 1) AS role_key
        FROM sys_user u
        LEFT JOIN sys_dept d ON u.dept_id = d.id
        ORDER BY u.id
""")
        List<SysUser> selectUserListWithRelation();

        @Select("""
        SELECT
            u.id,
            u.username,
            u.password,
            u.nick_name,
            u.dept_id,
            u.status,
            u.create_time,
            u.update_time,
            d.dept_name AS dept_name,
            (SELECT ur.role_id FROM sys_user_role ur WHERE ur.user_id = u.id LIMIT 1) AS role_id,
            (SELECT r.role_key FROM sys_user_role ur JOIN sys_role r ON ur.role_id = r.id WHERE ur.user_id = u.id LIMIT 1) AS role_key
        FROM sys_user u
        LEFT JOIN sys_dept d ON u.dept_id = d.id
        WHERE u.id = #{id}
""")
        SysUser selectUserByIdWithRelation(Long id);
}
