package com.example.saapp.vo;

import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import lombok.Data;

import java.util.List;

@Data
@TableName("sys_role")
public class SysRole {
    private Long id;
    private String roleKey;
    @TableField(exist = false)
    private List<Long> menuIds;
}