package com.example.saapp.vo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("sys_user")
public class SysUser {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String username;
    private String password;
    private String nickName;
    private Long deptId;
    private Integer status;

    @TableField(exist = false)
    private String deptName;

    @TableField(exist = false)
    private Long roleId;

    @TableField(exist = false)
    private String roleKey;

    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}