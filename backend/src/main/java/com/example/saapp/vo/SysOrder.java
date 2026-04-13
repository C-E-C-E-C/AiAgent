package com.example.saapp.vo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("sys_order")
public class SysOrder {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String orderNo;
    private Long empId;
    private BigDecimal totalAmount;
    private Integer orderStatus;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}