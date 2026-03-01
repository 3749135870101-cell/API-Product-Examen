import { IsString, IsNotEmpty, IsNumber, MinLength, Min, IsInt} from 'class-validator';

export class ProductDto {
    @IsNotEmpty()
    @MinLength(2)
    @IsString()
    name!: string;

    @IsNotEmpty()
    @IsString()
    description?: string;

    @IsNotEmpty()
    @IsNumber({ maxDecimalPlaces: 2 })
    @Min(0)
    price!: number;

    @IsNotEmpty()
    @IsInt()
    @Min(0)
    stock!: number;

}