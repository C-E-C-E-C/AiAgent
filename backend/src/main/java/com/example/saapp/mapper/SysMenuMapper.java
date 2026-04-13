package com.example.saapp.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.saapp.vo.SysMenu;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;
@Mapper
public interface SysMenuMapper extends BaseMapper<SysMenu> {
    @Select("SELECT m.perms " +
            "FROM sys_user u " +
            "JOIN sys_user_role ur ON u.id = ur.user_id " +
            "JOIN sys_role_menu rm ON ur.role_id = rm.role_id " +
            "JOIN sys_menu m ON rm.menu_id = m.id " +
            "WHERE u.id = #{userId}")
    List<String> selectPermsByUserId(Long userId);
}
