package com.example.saapp.vo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;

@Data
@TableName("sys_order_item")
public class SysOrderItem {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long orderId;
    private String productName;
    private Integer quantity;
    private BigDecimal price;
}