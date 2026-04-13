package com.example.saapp.vo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("sys_employee")
public class SysEmployee {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String empName;
    private Integer gender;
    private Integer age;
    private Long deptId;
    @TableField(exist = false)
    private String deptName;
    private BigDecimal salary;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}